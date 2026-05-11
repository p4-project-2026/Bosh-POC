from bosh.error_handler import BoshRuntimeError
from bosh.executor.function_binding import FunctionBinding

from . import *
from bosh.executor.environment import Environment
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

    def execute(self, env: Environment) -> None:
        value = self.value.execute(env)
        try:
            env.assign_variable(self.target.execute(env), value.execute(env))
        except Exception as e:
            raise BoshRuntimeError(f"Error assigning value to variable '{self.target.name}': {e}", self)
        return None


@dataclass
class AssignType(ASTNode):
    target: ASTNode
    var_type: str
    value: Optional[ASTNode]
    def accept(self, visitor) -> Any:
        return visitor.visit_AssignType(self)
    def execute(self, env: Environment) -> None:
        try:
            env.assign_variable(self.target.execute(env), self.value.execute(env) if self.value else None)
        except Exception as e:
            raise BoshRuntimeError(f"Error assigning value to variable '{self.target.name}': {e}", self)
        

@dataclass
class TaskDecl(ASTNode):
    name: str
    parameters: List[str]
    body: Block
    def accept(self, visitor) -> Any:
        return visitor.visit_TaskDecl(self)
    
    def execute(self, env: Environment) -> None:
        # Create a snapshot of the current variable scope stack to capture the environment for the function
        env_snapshot = env.snapshot()
        # Create a FunctionBinding for the task and bind it to the function table
        function_binding = FunctionBinding(parameters=self.parameters, body=self.body, env_snapshot=env_snapshot)
        try:
            env.bind_function(self.name, function_binding)
        except Exception as e:
            raise BoshRuntimeError(f"Error binding function '{self.name}': {e}", self)
        return None
