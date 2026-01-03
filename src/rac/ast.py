"""AST nodes for RAC."""

from datetime import date
from typing import Annotated, Any, Literal as TypingLiteral, Union

from pydantic import BaseModel, Field


# Expressions - using discriminated union for type safety
class Literal(BaseModel):
    type: TypingLiteral["literal"] = "literal"
    value: Any  # int, float, str, bool


class Var(BaseModel):
    """Variable reference (e.g., 'age' or 'gov/irs/standard_deduction')."""

    type: TypingLiteral["var"] = "var"
    path: str


class BinOp(BaseModel):
    type: TypingLiteral["binop"] = "binop"
    op: str  # +, -, *, /, >, <, >=, <=, ==, !=, and, or
    left: "Expr"
    right: "Expr"


class UnaryOp(BaseModel):
    type: TypingLiteral["unaryop"] = "unaryop"
    op: str  # -, not
    operand: "Expr"


class Call(BaseModel):
    """Function call (e.g., max(0, x), sum(members.income))."""

    type: TypingLiteral["call"] = "call"
    func: str
    args: list["Expr"]


class FieldAccess(BaseModel):
    """Field access on entity (e.g., members.income)."""

    type: TypingLiteral["field_access"] = "field_access"
    obj: "Expr"
    field: str


class Match(BaseModel):
    """Match expression."""

    type: TypingLiteral["match"] = "match"
    subject: "Expr"
    cases: list[tuple["Expr", "Expr"]]  # [(pattern, result), ...]
    default: "Expr | None" = None


class Cond(BaseModel):
    """Conditional expression (if/else)."""

    type: TypingLiteral["cond"] = "cond"
    condition: "Expr"
    then_expr: "Expr"
    else_expr: "Expr"


# Expression union type
Expr = Annotated[
    Union[Literal, Var, BinOp, UnaryOp, Call, FieldAccess, Match, Cond],
    Field(discriminator="type"),
]


# Declarations
class TemporalValue(BaseModel):
    """A value with temporal bounds."""

    start: date
    end: date | None = None  # None = no end
    expr: Expr


class VariableDecl(BaseModel):
    """Variable declaration."""

    path: str  # e.g., gov/irs/standard_deduction
    entity: str | None = None  # entity this applies to, or None for scalar
    values: list[TemporalValue] = []


class AmendDecl(BaseModel):
    """Amendment to an existing variable."""

    target: str  # path of variable being amended
    values: list[TemporalValue] = []


class EntityDecl(BaseModel):
    """Entity type declaration."""

    name: str
    fields: list[tuple[str, str]] = []  # [(name, type), ...]
    relations: list[tuple[str, str, bool]] = []  # [(name, target, many), ...]


class Module(BaseModel):
    """A parsed .rac file."""

    path: str = ""  # file path
    entities: list[EntityDecl] = []
    variables: list[VariableDecl] = []
    amendments: list[AmendDecl] = []


# Rebuild models for forward references
BinOp.model_rebuild()
UnaryOp.model_rebuild()
Call.model_rebuild()
FieldAccess.model_rebuild()
Match.model_rebuild()
Cond.model_rebuild()
TemporalValue.model_rebuild()
