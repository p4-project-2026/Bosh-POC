from dataclasses import dataclass
from typing import List, Any, Optional
from .ast_base import ASTNode, Block

# Statement nodes

@dataclass
class Assign(ASTNode):
    target: ASTNode
    value: ASTNode
    def accept(self, visitor) -> Any:
        return visitor.visit_Assign(self)


@dataclass
class AssignType(ASTNode):
    target: ASTNode
    var_type: str
    value: Optional[ASTNode]
    def accept(self, visitor) -> Any:
        return visitor.visit_AssignType(self)


@dataclass
class TaskDecl(ASTNode):
    name: str
    parameters: List[str]
    body: Block
    def accept(self, visitor) -> Any:
        return visitor.visit_TaskDecl(self)


@dataclass
class Print(ASTNode):
    expression: ASTNode
    def accept(self, visitor) -> Any:
        return visitor.visit_Print(self)


@dataclass
class IfElse(ASTNode):
    condition: ASTNode
    then_branch: Block
    else_branch: Optional[Block]
    def accept(self, visitor) -> Any:
        return visitor.visit_IfElse(self)


@dataclass
class Fallback(ASTNode):
    primary_stmt: ASTNode
    fallback_stmt: ASTNode
    def accept(self, visitor) -> Any:
        return visitor.visit_Fallback(self)


@dataclass
class ForAll(ASTNode):
    iterator_name: str
    iterable: ASTNode
    body: Block
    def accept(self, visitor) -> Any:
        return visitor.visit_ForAll(self)


@dataclass
class RepeatUntil(ASTNode):
    condition: ASTNode
    body: Block
    def accept(self, visitor) -> Any:
        return visitor.visit_RepeatUntil(self)


@dataclass
class Quit(ASTNode):
    def accept(self, visitor) -> Any:
        return visitor.visit_Quit(self)


@dataclass
class ListAdd(ASTNode):
    target: ASTNode
    item: ASTNode
    def accept(self, visitor) -> Any:
        return visitor.visit_ListAdd(self)


@dataclass
class ListRemove(ASTNode):
    target: ASTNode
    item: ASTNode
    def accept(self, visitor) -> Any:
        return visitor.visit_ListRemove(self)


@dataclass
class Return(ASTNode):
    expression: ASTNode
    def accept(self, visitor) -> Any:
        return visitor.visit_Return(self)
