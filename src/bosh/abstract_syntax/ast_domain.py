from . import *

# Domain-specific statements

@dataclass
class GoTo(ASTNode):
    path: ASTNode
    def accept(self, visitor) -> Any:
        return visitor.visit_GoTo(self)


@dataclass
class Make(ASTNode):
    entity_type: str
    name: str
    location: ASTNode
    def accept(self, visitor) -> Any:
        return visitor.visit_Make(self)


@dataclass
class Delete(ASTNode):
    target: ASTNode
    def accept(self, visitor) -> Any:
        return visitor.visit_Delete(self)


@dataclass
class Rename(ASTNode):
    target: ASTNode
    new_name: str
    def accept(self, visitor) -> Any:
        return visitor.visit_Rename(self)


@dataclass
class Copy(ASTNode):
    source: ASTNode
    target: ASTNode
    def accept(self, visitor) -> Any:
        return visitor.visit_Copy(self)


@dataclass
class Move(ASTNode):
    source: ASTNode
    target: ASTNode
    def accept(self, visitor) -> Any:
        return visitor.visit_Move(self)


@dataclass
class Read(ASTNode):
    source: ASTNode
    def accept(self, visitor) -> Any:
        return visitor.visit_Read(self)


@dataclass
class Write(ASTNode):
    target: ASTNode
    data: ASTNode
    def accept(self, visitor) -> Any:
        return visitor.visit_Write(self)


@dataclass
class GoUp(ASTNode):
    def accept(self, visitor) -> Any:
        return visitor.visit_GoUp(self)


@dataclass
class Execute(ASTNode):
    target: ASTNode
    def accept(self, visitor) -> Any:
        return visitor.visit_Execute(self)


@dataclass
class Pause(ASTNode):
    def accept(self, visitor) -> Any:
        return visitor.visit_Pause(self)


@dataclass
class Wait(ASTNode):
    time: ASTNode
    def accept(self, visitor) -> Any:
        return visitor.visit_Wait(self)


@dataclass
class Input(ASTNode):
    prompt: Optional[ASTNode]
    def accept(self, visitor) -> Any:
        return visitor.visit_Input(self)