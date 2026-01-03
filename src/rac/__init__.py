"""RAC: Rules as Code parser and executor."""

from datetime import date

from .ast import (
    AmendDecl,
    BinOp,
    Call,
    Cond,
    EntityDecl,
    Expr,
    FieldAccess,
    Literal,
    Match,
    Module,
    TemporalValue,
    UnaryOp,
    Var,
    VariableDecl,
)
from .compiler import IR, Compiler, CompileError, ResolvedVar
from .executor import Context, ExecutionError, Executor, Result, run
from .parser import Lexer, ParseError, Parser, parse, parse_file
from .schema import Entity, Field, Relation, Schema


def compile(modules: list[Module], as_of: date) -> IR:
    """Compile modules for a specific date."""
    return Compiler(modules).compile(as_of)


def execute(ir: IR, data: dict[str, list[dict]]) -> Result:
    """Execute compiled IR against data."""
    return run(ir, data)


__all__ = [
    "parse",
    "parse_file",
    "ParseError",
    "Lexer",
    "Parser",
    "Module",
    "EntityDecl",
    "VariableDecl",
    "AmendDecl",
    "TemporalValue",
    "Expr",
    "Literal",
    "Var",
    "BinOp",
    "UnaryOp",
    "Call",
    "FieldAccess",
    "Match",
    "Cond",
    "Schema",
    "Entity",
    "Field",
    "Relation",
    "compile",
    "Compiler",
    "CompileError",
    "IR",
    "ResolvedVar",
    "execute",
    "run",
    "Executor",
    "Context",
    "Result",
    "ExecutionError",
]
