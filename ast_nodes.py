# ast_nodes.py — los "nombres" de cada pieza del árbol.
# Son solo contenedores de datos (sin lógica) — el Evaluator después
# va a recorrer estos objetos y decidir qué hacer con cada tipo.
from dataclasses import dataclass
from typing import Optional


# ---- Expresiones (producen un valor) ----
@dataclass
class NumberLiteral:
    value: float

@dataclass
class BooleanLiteral:
    value: bool

@dataclass
class Identifier:
    name: str

@dataclass
class BinaryOp:
    left: object
    operator: str   # "+", "-", "*", "/", "<", ">", "=="
    right: object

@dataclass
class Call:
    callee: str      # nombre de la función, ej. "print"
    args: list


# ---- Statements (ejecutan una acción, no producen valor) ----
@dataclass
class LetStatement:
    name: str
    value: object

@dataclass
class ExpressionStatement:
    expr: object

@dataclass
class IfStatement:
    condition: object
    then_body: list
    else_body: Optional[list]

@dataclass
class WhileStatement:
    condition: object
    body: list

@dataclass
class FunctionDeclaration:
    name: str
    params: list
    body: list

@dataclass
class ReturnStatement:
    value: object

@dataclass
class AssignStatement:
    name: str
    value: object