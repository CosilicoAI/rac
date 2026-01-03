"""Compiler: resolves temporal layers and produces IR for backends.

The compiler takes parsed modules and an as_of date, resolves which
temporal values apply, and produces a flat variable graph.
"""

from datetime import date

from pydantic import BaseModel

from . import ast
from .schema import Entity, Field, Relation, Schema


class ResolvedVar(BaseModel):
    """A variable resolved to a single expression for a point in time."""

    path: str
    entity: str | None = None
    expr: ast.Expr
    deps: set[str] = set()  # paths of variables this depends on

    class Config:
        arbitrary_types_allowed = True


class IR(BaseModel):
    """Intermediate representation: resolved variable graph + schema."""

    schema_: Schema  # renamed to avoid conflict with pydantic
    variables: dict[str, ResolvedVar]
    order: list[str]  # topologically sorted variable paths

    class Config:
        arbitrary_types_allowed = True


class CompileError(Exception):
    pass


class Compiler:
    """Compiles parsed modules into IR."""

    def __init__(self, modules: list[ast.Module]):
        self.modules = modules
        self.schema = Schema()
        self.var_decls: dict[str, ast.VariableDecl] = {}
        self.amendments: list[ast.AmendDecl] = []

    def compile(self, as_of: date) -> IR:
        """Compile modules for a specific date."""
        # collect all declarations
        for module in self.modules:
            self._collect_entities(module)
            self._collect_variables(module)
            self._collect_amendments(module)

        # resolve temporal layers
        resolved = self._resolve_temporal(as_of)

        # compute dependencies
        for var in resolved.values():
            var.deps = self._find_deps(var.expr)

        # topological sort
        order = self._topo_sort(resolved)

        return IR(schema_=self.schema, variables=resolved, order=order)

    def _collect_entities(self, module: ast.Module) -> None:
        for decl in module.entities:
            entity = Entity(name=decl.name)
            for name, dtype in decl.fields:
                entity.fields[name] = Field(name=name, dtype=dtype)
            for name, target, many in decl.relations:
                entity.relations[name] = Relation(name=name, target=target, many=many)
            self.schema.add_entity(entity)

    def _collect_variables(self, module: ast.Module) -> None:
        for decl in module.variables:
            if decl.path in self.var_decls:
                raise CompileError(f"duplicate variable: {decl.path}")
            self.var_decls[decl.path] = decl

    def _collect_amendments(self, module: ast.Module) -> None:
        self.amendments.extend(module.amendments)

    def _resolve_temporal(self, as_of: date) -> dict[str, ResolvedVar]:
        """Resolve which temporal value applies for each variable."""
        resolved = {}

        for path, decl in self.var_decls.items():
            expr = self._pick_temporal(decl.values, as_of)
            if expr is None:
                raise CompileError(f"no value for {path} at {as_of}")
            resolved[path] = ResolvedVar(path=path, entity=decl.entity, expr=expr)

        # apply amendments (later amendments override earlier ones)
        for amend in self.amendments:
            if amend.target not in resolved:
                raise CompileError(f"amending unknown variable: {amend.target}")
            expr = self._pick_temporal(amend.values, as_of)
            if expr is not None:
                resolved[amend.target].expr = expr

        return resolved

    def _pick_temporal(
        self, values: list[ast.TemporalValue], as_of: date
    ) -> ast.Expr | None:
        """Pick the applicable temporal value for a date. Later values win."""
        result = None
        for tv in values:
            if tv.start <= as_of and (tv.end is None or as_of <= tv.end):
                result = tv.expr
        return result

    def _find_deps(self, expr: ast.Expr) -> set[str]:
        """Find all variable paths referenced in an expression."""
        deps: set[str] = set()
        self._walk_deps(expr, deps)
        return deps

    def _walk_deps(self, expr: ast.Expr, deps: set[str]) -> None:
        match expr:
            case ast.Literal():
                pass
            case ast.Var(path=path):
                if "/" in path:  # only track full paths, not local fields
                    deps.add(path)
            case ast.BinOp(left=left, right=right):
                self._walk_deps(left, deps)
                self._walk_deps(right, deps)
            case ast.UnaryOp(operand=operand):
                self._walk_deps(operand, deps)
            case ast.Call(args=args):
                for arg in args:
                    self._walk_deps(arg, deps)
            case ast.FieldAccess(obj=obj):
                self._walk_deps(obj, deps)
            case ast.Match(subject=subject, cases=cases, default=default):
                self._walk_deps(subject, deps)
                for pattern, result in cases:
                    self._walk_deps(result, deps)
                if default:
                    self._walk_deps(default, deps)
            case ast.Cond(condition=cond, then_expr=then_e, else_expr=else_e):
                self._walk_deps(cond, deps)
                self._walk_deps(then_e, deps)
                self._walk_deps(else_e, deps)

    def _topo_sort(self, variables: dict[str, ResolvedVar]) -> list[str]:
        """Topologically sort variables by dependencies."""
        visited: set[str] = set()
        order: list[str] = []
        temp: set[str] = set()

        def visit(path: str) -> None:
            if path in temp:
                raise CompileError(f"circular dependency involving {path}")
            if path in visited:
                return
            temp.add(path)
            if path in variables:
                for dep in variables[path].deps:
                    visit(dep)
            temp.remove(path)
            visited.add(path)
            order.append(path)

        for path in variables:
            visit(path)

        return order
