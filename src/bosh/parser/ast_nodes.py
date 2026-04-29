from dataclasses import dataclass
from typing import List, Any, Optional

# Laver dataklasser her og bruger dem i transformeren
# Gør det også nemmere at arbejde med AST'en senere i interpreter og analyzer

class ASTNode: pass

@dataclass
class Program(ASTNode):
    # Betyder at det er en liste af statements, og hver statement er en ASTNode (f.eks. PrintStatement, VarDeclaration, etc.) *mangler implementering
    statements: List[ASTNode]

@dataclass
class Block(ASTNode):
    statements: List[ASTNode]

# Definitions ----------------------------------------

@dataclass
class Assign(ASTNode):
    target: ASTNode
    value: ASTNode

@dataclass
class AssignType(ASTNode):
    target: ASTNode
    var_type: str
    value: Optional[ASTNode]

@dataclass
class TaskDecl(ASTNode):
    name: str
    parameters: List[str]
    body: Block

# General Statements ----------------------------------------

@dataclass
class Print(ASTNode):
    expression: ASTNode

@dataclass
class IfElse(ASTNode):
    condition: ASTNode
    then_branch: Block
    else_branch: Optional[Block]

@dataclass
class Fallback(ASTNode):
    primary_stmt: ASTNode
    fallback_stmt: ASTNode

@dataclass
class ForAll(ASTNode):
    iterator_name: str
    iterable: ASTNode
    body: Block

@dataclass
class RepeatUntil(ASTNode):
    condition: ASTNode
    body: Block

@dataclass
class Quit(ASTNode):
    pass

@dataclass
class ListAdd(ASTNode):
    target: ASTNode
    item: ASTNode

@dataclass
class ListRemove(ASTNode):
    target: ASTNode
    item: ASTNode

@dataclass
class Return(ASTNode):
    expression: ASTNode

# Domain Statements ----------------------------------------

@dataclass
class GoTo(ASTNode):
    path: ASTNode

@dataclass
class Make(ASTNode):
    entity_type: str
    name: str
    location: ASTNode

@dataclass
class Delete(ASTNode):
    target: ASTNode

@dataclass
class Rename(ASTNode):
    target: ASTNode
    new_name: str

@dataclass
class Copy(ASTNode):
    source: ASTNode
    target: ASTNode

@dataclass # NY. VI BURDE HAVE DEN I GRAMMAR
class Move(ASTNode):
    source: ASTNode
    target: ASTNode

@dataclass # NY. VI BURDE HAVE DEN I GRAMMAR
class Read(ASTNode):
    source: ASTNode

@dataclass # NY. VI BURDE HAVE DEN I GRAMMAR
class Write(ASTNode):
    target: ASTNode
    data: ASTNode

# Expressions ----------------------------------------

@dataclass
class NumberLiteral(ASTNode):
    value: float

@dataclass
class DecimalLiteral(ASTNode):
    value: float

@dataclass
class StringLiteral(ASTNode):
    value: str

@dataclass
class InterpolatedString(ASTNode):
    parts: List[ASTNode]

@dataclass
class BooleanLiteral(ASTNode):
    value: bool

@dataclass
class NullLiteral(ASTNode):
    pass

@dataclass
class ListLiteral(ASTNode):
    elements: List[ASTNode]

@dataclass
class ListLookup(ASTNode):
    target: ASTNode
    index: ASTNode

@dataclass
class Identifier(ASTNode):
    name: str

@dataclass
class TaskIdentifier(ASTNode):
    name: str

@dataclass
class TaskCall(ASTNode):
    name: str
    arguments: List[ASTNode]

@dataclass
class BinaryOp(ASTNode):
    left: ASTNode
    operator: str
    right: ASTNode

@dataclass
class UnaryOp(ASTNode):
    operator: str
    operand: ASTNode

@dataclass
class AccessOp(ASTNode):
    target: ASTNode
    operation: str
    argument: Optional[ASTNode] = None