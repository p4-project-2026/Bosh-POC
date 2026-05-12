from .ast_base import *

@dataclass
class NumberLiteral(ASTNode):
    value: float
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        return "number"
    
    def execute(self, env: Environment) -> float:
        return self.value


@dataclass
class DecimalLiteral(ASTNode):
    value: float
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        return "decimal"
    
    def execute(self, env: Environment) -> float:
        return self.value


@dataclass
class StringLiteral(ASTNode):
    value: str
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        return "text"

    def execute(self, env: Environment) -> str:
        return self.value


@dataclass
class InterpolatedString(ASTNode):
    parts: List[ASTNode]
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        for part in self.parts:
            if part.check(v_table, f_table) is None:
                raise BoshTypeError("Undefined variable in interpolated string", self)
        return "text"

    def execute(self, env: Environment) -> str:
        result = ""
        for part in self.parts:
            value = part.execute(env)
            result += str(value)
        return result
    
@dataclass
class BooleanLiteral(ASTNode):
    value: bool
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        return "boolean"

    def execute(self, env: Environment) -> bool:
        return self.value


@dataclass
class NullLiteral(ASTNode):
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        return "null"
    def execute(self, env: Environment) -> None:
        return None


@dataclass
class ListLiteral(ASTNode):
    elements: List[ASTNode]
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        if len(self.elements) == 0:
            return "list<any>"
        element_type = self.elements[0].check(v_table, f_table)
        for elem in self.elements[1:]:
            elem_type = elem.check(v_table, f_table)
            if elem_type != element_type:
                raise BoshTypeError(f"List elements must all be of the same type, expected {element_type}, got {elem_type}", self)
        return f"list<{element_type}>"

    def execute(self, env: Environment) -> List[Any]:
        return [elem.execute(env) for elem in self.elements]

@dataclass
class Identifier(ASTNode):
    name: str
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        try:
            var_type = v_table.lookup(self.name)
        except Exception:
            raise BoshTypeError(f"Undefined variable '{self.name}'", self)
        return var_type

    def execute(self, env: Environment) -> Any:
        try:
            value = env.lookup_variable(self.name)
        except Exception:
            raise BoshRuntimeError(f"Undefined variable '{self.name}'", self)
        return value


@dataclass
class TaskIdentifier(ASTNode):
    name: str
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        try:
            var_type = f_table.lookup(self.name) # Typechecker.py is different but I think this is correct. No var_type was defined
        except Exception:
            raise BoshTypeError(f"Undefined task '{self.name}'", self)
        return var_type
    
    def execute(self, env: Environment) -> None:
        try:
            value = env.lookup_task(self.name)
        except Exception:
            raise BoshRuntimeError(f"Undefined task '{self.name}'", self)
        return value
        


@dataclass
class TaskCall(ASTNode):
    name: str
    arguments: Optional[List[ASTNode]] = None
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        try:
            signature = f_table.lookup(self.name)
        except Exception:
            raise BoshTypeError(f"Undefined task '{self.name}'", self)
        
        if len(self.arguments) != len(signature.param_types):
            raise BoshTypeError(f"Task '{self.name}' expects {len(signature.param_types)} arguments, but {len(self.arguments)} were provided.", self)
        for i, arg in enumerate(self.arguments):
            if i < len(signature.param_types):
                arg_type = arg.check(v_table, f_table)
                expected_type = signature.param_types[signature.param[i]]
                if arg_type != expected_type and expected_type != "any":
                    raise BoshTypeError(f"Argument {i+1} of task '{self.name}' expects type '{expected_type}', but got '{arg_type}'.", self)
        return signature.return_type

    def execute(self, env: Environment) -> Any:
        try:
            task_func = env.enter_function_scope(self.name)
        except Exception as e:
            raise BoshRuntimeError(f"error executing task '{self.name}': {e}", self)
        for i in range(len(task_func.parameters)):
            try:
                env.assign_variable(task_func.parameters[i], self.arguments[i].execute(env))
            except Exception as e:
                raise BoshRuntimeError(f"Error assigning argument {i+1} for task '{self.name}': {e}", self)
        return_value = task_func.execute(env)
        env.exit_function_scope()
        return return_value

    def execute(self, env: Environment) -> Any:
        try:
            task_func = env.enter_function_scope(self.name)
        except Exception as e:
            raise BoshRuntimeError(f"error executing task '{self.name}': {e}", self)
        for i in range(len(task_func.parameters)):
            try:
                env.assign_variable(task_func.parameters[i], self.arguments[i].execute(env))
            except Exception as e:
                raise BoshRuntimeError(f"Error assigning argument {i+1} for task '{self.name}': {e}", self)
        return_value = task_func.execute(env)
        env.exit_function_scope()
        return return_value


@dataclass
class ListLookup(ASTNode):
    target: ASTNode
    index: ASTNode
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        target_type = self.target.check(v_table, f_table)
        index_type = self.index.check(v_table, f_table)
        if target_type != "list":
            raise BoshTypeError(f"Cannot index type '{target_type}'. Expected a list.", self)
        if index_type != "number":
            raise BoshTypeError(f"List index must be of type 'number', got '{index_type}'", self)
        

@dataclass
class Unit(ASTNode):
    target: ASTNode
    unit_type: str

    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        target_type = self.target.check(v_table, f_table)
        if target_type not in ["number", "decimal"]:
            raise BoshTypeError(f"Cannot apply unit '{self.unit_type}' to type '{target_type}'. Expected number or decimal.", self)
        
        return f"{target_type}_{self.unit_type}"


@dataclass
class BinaryOp(ASTNode):
    left: ASTNode
    operator: str
    right: ASTNode
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        left_type = self.left.check(v_table, f_table)
        right_type = self.right.check(v_table, f_table)
        op = self.operator

        if op in ["plus", "minus", "div", "mult", "mod"]:
            if left_type in ["int", "decimal"] and right_type in ["int", "decimal"] or left_type == right_type == "any":
                return left_type
            else:
                raise BoshTypeError(f"Operator '{op}' not supported for types '{left_type}' and '{right_type}'", self)
        elif op in ["eq", "neq"]:
            return "boolean"
        elif op in ["or", "and"]:
            return "boolean"
        elif op in ["lt", "gt", "gte", "lte"]:
            return "boolean"
        else:
            raise BoshTypeError(f"Unsupported operator '{op}'", self)

        def execute(self, env: Environment) -> Any:
            match self.operator:
                case "plus":
                    return self.left.execute(env) + self.right.execute(env)
                case "minus":
                    return self.left.execute(env) - self.right.execute(env)
                case "mult":
                    return self.left.execute(env) * self.right.execute(env)
                case "div":
                    return self.left.execute(env) / self.right.execute(env)
                case "mod":
                    return self.left.execute(env) % self.right.execute(env)
                case "eq":
                    return self.left.execute(env) == self.right.execute(env)
                case "neq":
                    return self.left.execute(env) != self.right.execute(env)
                case "or":
                    return self.left.execute(env) or self.right.execute(env)
                case "and":
                    return self.left.execute(env) and self.right.execute(env)
                case "lt":
                    return self.left.execute(env) < self.right.execute(env)
                case "gt":
                    return self.left.execute(env) > self.right.execute(env)
                case "lte":
                    return self.left.execute(env) <= self.right.execute(env)
                case "gte":
                    return self.left.execute(env) >= self.right.execute(env)
                case _:
                    raise BoshRuntimeError(f"Unsupported operator '{self.operator}'", self)

@dataclass
class UnaryOp(ASTNode):
    operator: str
    operand: ASTNode
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        operand_type = self.operand.check(v_table, f_table)
        op = self.operator
        if op == "-":
            if operand_type not in ["number", "decimal"]:
                raise BoshTypeError(f"Unary operator '{op}' not supported for type '{operand_type}'. Expected 'number' or 'decimal'.", self)
        elif op == "not":
            if operand_type != "boolean":
                raise BoshTypeError(f"Unary operator '{op}' not supported for type '{operand_type}'. Expected 'boolean'.", self)
        elif op == "first":
            if operand_type.startswith("list"):
                return operand_type[5:-1]  # Extract the element type from "list<element_type>"
            else:
                raise BoshTypeError(f"Unary operator '{op}' not supported for type '{operand_type}'. Expected a list.", self)

    def execute(self, env):
        match self.operator:
            case "-":
                return -self.operand.execute(env)
            case "not":
                return not self.operand.execute(env)
            case "plus":  # Unary plus, just returns the operand
                return self.operand.execute(env)
            
            case _:
                raise BoshRuntimeError(f"Unsupported unary operator '{self.operator}'", self)

@dataclass
class AccessOp(ASTNode):
    target: ASTNode
    operation: str
    argument: Optional[ASTNode] = None
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        op = self.operation
        if op == "ends_with":
            return "boolean"
        elif op == "here":
            return "folder"
        elif op == "now":
            return "time"
        else:
            raise BoshTypeError(f"Unsupported access operation '{op}'", self)
        
