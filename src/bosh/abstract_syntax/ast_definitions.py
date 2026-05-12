from .ast_base import *
from bosh.error_handler import BoshTypeError, BoshRuntimeError
from bosh.executor.function_binding import FunctionBinding
from bosh.executor.environment import Environment
from bosh.abstract_syntax.ast_expressions import Identifier

@dataclass
class Assign(ASTNode):
    target: Identifier
    value: ASTNode
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> None:
        value_type = self.value.check(v_table, f_table)

        if value_type is None:
            raise BoshTypeError(f"Value assigned to '{self.target.name}' is undefined.", self)

        try:
            v_table.bind(self.target.name, value_type)
        except Exception as e:
            raise BoshTypeError(str(e), self)

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
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> None:
        value_type = self.value.check(v_table, f_table) if self.value else None
        if value_type and value_type != self.var_type:
            raise BoshTypeError(f"Cannot assign value of type '{value_type}' to variable '{self.target.name}' of type '{self.var_type}'", self)

        try:
            v_table.bind(self.target.name, self.var_type)
        except Exception as e:
            raise BoshTypeError(str(e), self)
            
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
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> None:
        param_types = {param: "any" for param in self.parameters}
        signature = FunctionSignature(parameters=param_types, return_type="any")

        try:
            f_table.bind(self.name, signature)
        except:
            raise BoshTypeError(f"Task '{self.name}' is already defined.", self)
        
        v_table.new_scope()
        try:
            for param in self.parameters:
                v_table.bind(param, "any")
            body_type = self.body.check(v_table, f_table)
            signature.return_type = body_type if body_type else "any"
        except Exception as e:
            raise BoshTypeError(str(e), self)
        finally:
            try:
                v_table.exit_scope()
            except Exception as e:
                raise BoshTypeError(str(e), self)
            
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
