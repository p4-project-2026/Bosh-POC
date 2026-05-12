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


@dataclass
class ListLookup(ASTNode):
    target: ASTNode
    index: ASTNode
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        target_type = self.target.check(v_table, f_table)
        index_type = self.index.check(v_table, f_table)
        if not target_type.startswith("list<") or not target_type.endswith(">"):
            raise BoshTypeError(f"Cannot index type '{target_type}'. Expected a list.", self)
        if index_type != "number":
            raise BoshTypeError(f"List index must be of type 'number', got '{index_type}'", self)
        return target_type[5:-1]
    
    def execute(self, env: Environment) -> Any:
        try:
            target_value = self.target.execute(env)
        except Exception as e:
            raise BoshRuntimeError(f"Error executing list lookup: {e}", self)
        index_value = self.index.execute(env)
        try:
            return target_value[int(index_value)]
        except Exception as e:
            raise BoshRuntimeError(f"Error executing list lookup: {e}", self)

@dataclass
class Unit(ASTNode):
    target: ASTNode
    unit_type: str

    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        target_type = self.target.check(v_table, f_table)
        if target_type not in ["number", "decimal"]:
            raise BoshTypeError(f"Cannot apply unit '{self.unit_type}' to type '{target_type}'. Expected number or decimal.", self)
        return "time"

    def execute(self, env: Environment) -> Any:
        target_value = self.target.execute(env)
        match self.unit_type:
            case "seconds":
                return target_value * 1000  # Convert seconds to milliseconds
            case "minutes":
                return target_value * 60 * 1000  # Convert minutes to milliseconds
            case "hours":
                return target_value * 60 * 60 * 1000  # Convert hours to milliseconds
            case "days":
                return target_value * 24 * 60 * 60 * 1000  # Convert days to milliseconds
            case "weeks":
                return target_value * 7 * 24 * 60 * 60 * 1000  # Convert weeks to milliseconds
            case "months":
                return target_value * 30 * 24 * 60 * 60 * 1000  # Approximate conversion of months to milliseconds
            case "years":
                return target_value * 365 * 24 * 60 * 60 * 1000  # Approximate conversion of years to milliseconds
            case _:
                raise BoshRuntimeError(f"Unsupported unit type '{self.unit_type}'", self)

@dataclass
class BinaryOp(ASTNode):
    left: ASTNode
    operator: str
    right: ASTNode
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        left_type = self.left.check(v_table, f_table) if isinstance(self.left, ASTNode) else self.left
        right_type = self.right.check(v_table, f_table) if isinstance(self.right, ASTNode) else self.right
        op = self.operator

        if left_type == "any" or right_type == "any":
            if op in ["eq", "neq", "lt", "gt", "gte", "lte", "or", "and"]:
                return "boolean"
            if op in ["plus", "minus", "div", "mult", "mod"]:
                return "any"
            # fallback: preserve previous behavior for unknown operators
            return "any" 
        
        if op in ["plus", "minus", "div", "mult", "mod"]:
            if left_type in ["number", "decimal"] and right_type in ["number", "decimal"]:
                return "decimal" if "decimal" in [left_type, right_type] else "number"
            elif op == "plus" and left_type == "text" and right_type == "text":
                return "text"
            else:
                raise BoshTypeError(f"Operator '{op}' not supported for types '{left_type}' and '{right_type}'", self)
            
        elif op in ["eq", "neq"]:
            numeric_eq = (left_type in ["number", "decimal"] and right_type in ["number", "decimal"])
            null_eq = (left_type == "null" or right_type == "null")
            if left_type != right_type and not numeric_eq and not null_eq:
                raise BoshTypeError(f"Operator '{op}' not supported for types '{left_type}' and '{right_type}'", self)
            return "boolean"
        
        elif op in ["or", "and"]:
            if left_type != "boolean" or right_type != "boolean":
                raise BoshTypeError(f"Logical operator '{op}' requires boolean operands, got '{left_type}' and '{right_type}'", self)
            return "boolean"
        
        elif op in ["lt", "gt", "gte", "lte"]:
            if left_type not in ["number", "decimal", "date", "time"] or right_type not in ["number", "decimal", "date", "time"]:
                raise BoshTypeError(f"Relational operator '{op}' requires numeric or temporal operands, got '{left_type}' and '{right_type}'.", self)
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
        if op in ["-", "neg", "negative"]:
            if operand_type not in ["number", "decimal"]:
                raise BoshTypeError(f"Unary operator '{op}' not supported for type '{operand_type}'. Expected 'number' or 'decimal'.", self)
            return operand_type
        
        elif op in ["not_", "not", "!"]:
            if operand_type != "boolean":
                raise BoshTypeError(f"Unary operator '{op}' not supported for type '{operand_type}'. Expected 'boolean'.", self)
            return "boolean"
        
        elif op in ["floor", "ceiling", "round"]:
            if operand_type not in ["number", "decimal"]:
                raise BoshTypeError(f"Unary operator '{op}' not supported for type '{operand_type}'. Expected 'number' or 'decimal'.", self)
            return "number"
        
        elif op == "exponent":
            if operand_type not in ["number", "decimal"]:
                raise BoshTypeError(f"Unary operator 'exponent' not supported for type '{operand_type}'. Expected 'number' or 'decimal'.", self)
            return "decimal"
        
        elif op == "length":
            is_list = isinstance(operand_type, str) and operand_type.startswith("list<") and operand_type.endswith(">")
            if operand_type != "text" and not is_list:
                raise BoshTypeError(f"Unary operator 'length' not supported for type '{operand_type}'. Expected 'text' or 'list'.", self)
            return "number"
    
        elif op in ["first", "last"]:
            is_list = isinstance(operand_type, str) and operand_type.startswith("list<") and operand_type.endswith(">")
            if operand_type != "text" and not is_list:
                raise BoshTypeError(f"Unary operator '{op}' not supported for type '{operand_type}'. Expected 'text' or 'list'.", self)
            if operand_type == "text":
                return "text"
            else:
                return operand_type[5:-1]
            
        else:
            raise BoshTypeError(f"Unsupported unary operator '{op}'", self)

    def execute(self, env):
        import math
        match self.operator:
            case "-":
                return -self.operand.execute(env)
            case "not":
                return not self.operand.execute(env)
            case "first":
                return self.operand.execute(env)[0]
            case "last":
                return self.operand.execute(env)[-1]
            case "floor":
                return math.floor(self.operand.execute(env))
            case "ceiling":
                return math.ceil(self.operand.execute(env))
            case "exponent":
                return math.exp(self.operand.execute(env))
            case "round":
                return int(round(self.operand.execute(env)))
            case _:
                raise BoshRuntimeError(f"Unsupported unary operator '{self.operator}'", self)

@dataclass
class AccessOp(ASTNode):
    target: Optional[ASTNode]
    operation: str
    argument: Optional[ASTNode] = None
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        target_type = self.target.check(v_table, f_table) if self.target else None
        op = self.operation

        if op == "file_name":
            if target_type != "text":
                raise BoshTypeError(f"Cannot get file name of type '{target_type}'. Expected 'file' or 'folder'.", self)
            return "text"
        
        elif op == "age":
            if target_type != "text":
                raise BoshTypeError(f"Cannot get age of type '{target_type}'. Expected 'file' or 'folder'.", self)
            return "number"
        
        elif op in ["starts_with", "ends_with", "regex"]:
            if target_type != "text":
                raise BoshTypeError(f"Cannot apply operation '{op}' to type '{target_type}'. Expected 'text'.", self)

            if self.argument is not None:
                arg_type = self.argument.check(v_table, f_table)
                if arg_type != "text":
                    raise BoshTypeError(f"Argument for operation '{op}' must be of type 'text', got '{arg_type}'.", self)
            return "boolean"
        
        elif op == "unit":
            if target_type in ["number", "decimal"]:
                return "time"
            elif target_type == "time":
                return "number"
            else:
                raise BoshTypeError(f"Time units require a numeric, date, or time target, got '{target_type}'.", self)
        
        elif op == "now":
            return "date"
        
        elif op == "here":
            return "text"
        
        else:
            raise BoshTypeError(f"Unsupported access operation '{op}'", self)