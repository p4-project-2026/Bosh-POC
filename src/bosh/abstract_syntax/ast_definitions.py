from . import *

@dataclass
class Assign(ASTNode):
    target: 'Identifier'
    value: ASTNode
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        value_type = self.value.check(v_table, f_table)

        if value_type is None:
            raise BoshTypeError(f"Value assigned to '{self.target.name}' is undefined.", self)

        try:
            v_table.bind(self.target.name, value_type)
        except Exception as e:
            raise BoshTypeError(str(e), self)

    def execute(self, env: 'Environment') -> Any:
        pass


@dataclass
class AssignType(ASTNode):
    target: ASTNode
    var_type: str
    value: Optional[ASTNode]
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        value_type = self.value.check(v_table, f_table)
        if value_type and value_type != self.var_type:
            raise BoshTypeError(f"Cannot assign value of type '{value_type}' to variable '{self.target.name}' of type '{self.var_type}'", self)

        try:
            v_table.bind(self.target.name, self.var_type)
        except Exception as e:
            raise BoshTypeError(str(e), self)
        
    
@dataclass
class TaskDecl(ASTNode):
    name: str
    parameters: List[str]
    body: Block
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        param_types = ["any"] * len(self.parameters)
        signature = FunctionSignature(param_types=param_types, return_type="any") #SOMETHING WRONG HERE

        try:
            self.f_table.bind(self.name, signature)
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