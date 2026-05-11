from . import *

@dataclass
class Assign(ASTNode):
    target: 'Identifier'
    value: ASTNode
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        value_type = self.value.check(v_table, f_table)

        if value_type is None:
            raise BoshTypeError(f"Value assigned to '{self.target.name}' is undefined.", self)

        v_table.bind(self.target.name, value_type)
        return None

    def execute(self, env: Environment) -> Any:
        pass


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
