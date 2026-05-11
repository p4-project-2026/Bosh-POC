from . import *

# Expression and literal nodes

@dataclass
class NumberLiteral(ASTNode):
    value: float
    def accept(self, visitor) -> Any:
        return visitor.visit_NumberLiteral(self)
    
    def execute(self, env: Environment) -> float:
        return self.value


@dataclass
class DecimalLiteral(ASTNode):
    value: float
    def accept(self, visitor) -> Any:
        return visitor.visit_DecimalLiteral(self)
    
    def execute(self, env: Environment) -> float:
        return self.value


@dataclass
class StringLiteral(ASTNode):
    value: str
    def accept(self, visitor) -> Any:
        return visitor.visit_StringLiteral(self)

    def execute(self, env: Environment) -> str:
        return self.value


@dataclass
class InterpolatedString(ASTNode):
    parts: List[ASTNode]
    def accept(self, visitor) -> Any:
        return visitor.visit_InterpolatedString(self)

    def execute(self, env: Environment) -> str:
        result = ""
        for part in self.parts:
            value = part.execute(env)
            result += str(value)
        return result
    
@dataclass
class BooleanLiteral(ASTNode):
    value: bool
    def accept(self, visitor) -> Any:
        return visitor.visit_BooleanLiteral(self)

    def execute(self, env: Environment) -> bool:
        return self.value


@dataclass
class NullLiteral(ASTNode):
    def accept(self, visitor) -> Any:
        return visitor.visit_NullLiteral(self)


@dataclass
class ListLiteral(ASTNode):
    elements: List[ASTNode]
    def accept(self, visitor) -> Any:
        return visitor.visit_ListLiteral(self)


@dataclass
class Identifier(ASTNode):
    name: str
    def accept(self, visitor) -> Any:
        return visitor.visit_Identifier(self)


@dataclass
class TaskIdentifier(ASTNode):
    name: str
    def accept(self, visitor) -> Any:
        return visitor.visit_TaskIdentifier(self)


@dataclass
class TaskCall(ASTNode):
    name: str
    arguments: Optional[List[ASTNode]] = None
    def accept(self, visitor) -> Any:
        return visitor.visit_TaskCall(self)


@dataclass
class ListLookup(ASTNode):
    target: ASTNode
    index: ASTNode
    def accept(self, visitor) -> Any:
        return visitor.visit_ListLookup(self)


@dataclass
class BinaryOp(ASTNode):
    left: ASTNode
    operator: str
    right: ASTNode
    def accept(self, visitor) -> Any:
        return visitor.visit_BinaryOp(self)


@dataclass
class UnaryOp(ASTNode):
    operator: str
    operand: ASTNode
    def accept(self, visitor) -> Any:
        return visitor.visit_UnaryOp(self)


@dataclass
class AccessOp(ASTNode):
    target: ASTNode
    operation: str
    argument: Optional[ASTNode] = None
    def accept(self, visitor) -> Any:
        return visitor.visit_AccessOp(self)
