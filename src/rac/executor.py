"""Executor: evaluates compiled IR against input data."""

from typing import Any

from pydantic import BaseModel

from . import ast
from .compiler import IR


class ExecutionError(Exception):
    pass


class Context(BaseModel):
    """Runtime context for evaluation."""

    data: dict[str, list[dict]]  # entity_name -> rows
    computed: dict[str, Any] = {}  # path -> value
    current_entity: dict | None = None  # when evaluating entity-scoped vars

    class Config:
        arbitrary_types_allowed = True

    def get(self, path: str) -> Any:
        """Get a value by path. Checks computed first, then current entity."""
        if path in self.computed:
            return self.computed[path]
        if self.current_entity and path in self.current_entity:
            return self.current_entity[path]
        raise ExecutionError(f"undefined: {path}")


BUILTINS = {
    "min": min,
    "max": max,
    "abs": abs,
    "round": round,
    "sum": sum,
    "len": len,
    "clip": lambda x, lo, hi: max(lo, min(hi, x)),
}


def evaluate(expr: ast.Expr, ctx: Context) -> Any:
    """Evaluate an expression in context."""
    match expr:
        case ast.Literal(value=v):
            return v

        case ast.Var(path=path):
            return ctx.get(path)

        case ast.BinOp(op=op, left=left, right=right):
            l = evaluate(left, ctx)
            r = evaluate(right, ctx)
            match op:
                case "+":
                    return l + r
                case "-":
                    return l - r
                case "*":
                    return l * r
                case "/":
                    return l / r if r != 0 else 0
                case "<":
                    return l < r
                case ">":
                    return l > r
                case "<=":
                    return l <= r
                case ">=":
                    return l >= r
                case "==":
                    return l == r
                case "!=":
                    return l != r
                case "and":
                    return l and r
                case "or":
                    return l or r
                case _:
                    raise ExecutionError(f"unknown op: {op}")

        case ast.UnaryOp(op=op, operand=operand):
            v = evaluate(operand, ctx)
            match op:
                case "-":
                    return -v
                case "not":
                    return not v
                case _:
                    raise ExecutionError(f"unknown unary op: {op}")

        case ast.Call(func=func, args=args):
            if func not in BUILTINS:
                raise ExecutionError(f"unknown function: {func}")
            arg_vals = [evaluate(a, ctx) for a in args]
            return BUILTINS[func](*arg_vals)

        case ast.FieldAccess(obj=obj, field=fld):
            o = evaluate(obj, ctx)
            if isinstance(o, dict):
                return o.get(fld)
            if isinstance(o, list):
                return [
                    item.get(fld) if isinstance(item, dict) else getattr(item, fld)
                    for item in o
                ]
            return getattr(o, fld)

        case ast.Match(subject=subject, cases=cases, default=default):
            val = evaluate(subject, ctx)
            for pattern, result in cases:
                pattern_val = evaluate(pattern, ctx)
                if val == pattern_val:
                    return evaluate(result, ctx)
            if default:
                return evaluate(default, ctx)
            raise ExecutionError(f"no match for: {val}")

        case ast.Cond(condition=cond, then_expr=then_e, else_expr=else_e):
            if evaluate(cond, ctx):
                return evaluate(then_e, ctx)
            return evaluate(else_e, ctx)

        case _:
            raise ExecutionError(f"unknown expr type: {type(expr)}")


class Result(BaseModel):
    """Execution result."""

    values: dict[str, Any]  # path -> computed value
    entity_values: dict[str, dict[str, list[Any]]]  # entity -> path -> values per row

    class Config:
        arbitrary_types_allowed = True


class Executor:
    """Executes compiled IR against data."""

    def __init__(self, ir: IR):
        self.ir = ir

    def execute(self, data: dict[str, list[dict]]) -> Result:
        """Execute the IR against input data."""
        errors = self.ir.schema_.validate_data(data)
        if errors:
            raise ExecutionError(f"invalid data: {errors}")

        ctx = Context(data=data)
        entity_values: dict[str, dict[str, list[Any]]] = {}

        for path in self.ir.order:
            var = self.ir.variables[path]

            if var.entity is None:
                ctx.computed[path] = evaluate(var.expr, ctx)
            else:
                entity_name = var.entity
                if entity_name not in data:
                    raise ExecutionError(f"missing entity data: {entity_name}")

                if entity_name not in entity_values:
                    entity_values[entity_name] = {}
                entity_values[entity_name][path] = []

                for row in data[entity_name]:
                    ctx.current_entity = row
                    val = evaluate(var.expr, ctx)
                    entity_values[entity_name][path].append(val)
                    ctx.current_entity = None

        return Result(values=ctx.computed, entity_values=entity_values)


def run(ir: IR, data: dict[str, list[dict]]) -> Result:
    """Execute IR against data."""
    return Executor(ir).execute(data)
