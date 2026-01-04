"""RAC: Rules as Code parser, compiler, and executor."""

from datetime import date

from .ast import (
    AmendDecl,
    BinOp,
    Call,
    Cond,
    EntityDecl,
    Expr,
    FieldAccess,
    ImportDecl,
    Literal,
    Match,
    Module,
    RepealDecl,
    TemporalValue,
    UnaryOp,
    Var,
    VariableDecl,
)
from .codegen import generate_rust
from .compiler import IR, Compiler, CompileError, ResolvedVar
from .executor import Context, ExecutionError, Executor, Result, run
from .model import CompareResult, Model, RunResult
from .native import CompiledBinary, compile_to_binary
from .parser import Lexer, ParseError, Parser, parse, parse_file
from .schema import Data, Entity, Field, ForeignKey, ReverseRelation, Schema


def compile(modules: list[Module], as_of: date) -> IR:
    """Compile modules for a specific date."""
    return Compiler(modules).compile(as_of)


def execute(ir: IR, data: dict[str, list[dict]] | Data) -> Result:
    """Execute compiled IR against data."""
    return run(ir, data)


__all__ = [
    # Parse
    "parse",
    "parse_file",
    "ParseError",
    "Lexer",
    "Parser",
    # AST
    "Module",
    "EntityDecl",
    "VariableDecl",
    "AmendDecl",
    "RepealDecl",
    "ImportDecl",
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
    # Schema
    "Schema",
    "Entity",
    "Field",
    "ForeignKey",
    "ReverseRelation",
    "Data",
    # Compile
    "compile",
    "Compiler",
    "CompileError",
    "IR",
    "ResolvedVar",
    # Execute
    "execute",
    "run",
    "Executor",
    "Context",
    "Result",
    "ExecutionError",
    # Codegen
    "generate_rust",
    # Native compilation
    "compile_to_binary",
    "CompiledBinary",
    # High-level interface
    "Model",
    "RunResult",
    "CompareResult",
]
