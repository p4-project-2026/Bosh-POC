from typing import Optional
import bosh.parser.ast_nodes as ast
from .symbol_table import SymbolTable

class TypeChecker:
    def __init__(self):
        self.v_table = SymbolTable(str)

    def check(self, node: ast.ASTNode) -> Optional[str]:
        return node.accept(self)

    def general_visit(self, node: ast.ASTNode) -> Optional[str]:
        print(f"Type checking not implemented for node type: {type(node).__name__}")
        return None

    def visit_Program(self, node: ast.Program) -> Optional[str]:
        return node.block.accept(self)

    def visit_Block(self, node: ast.Block) -> Optional[str]:
        for stmt in node.statements:
            stmt.accept(self)

    # Definitions ----------------------------------------

    def visit_Assign(self, node: ast.Assign) -> Optional[str]:
        var_name = node.target.name
        value_type = node.value.accept(self)

        if value_type is not None:
            if self.v_table.lookup(var_name):
                self.v_table.set(var_name, value_type)
            else:
                self.v_table.bind(var_name, value_type)
        return value_type

    def visit_AssignType(self, node: ast.AssignType) -> Optional[str]:
        # Checks that the assigned value matches the declared type, and registers the variable with that type
        var_name = node.target.name
        var_type = node.var_type
        value_type = node.value.accept(self) if node.value else None
        if value_type and value_type != var_type:
            print(f"Type error: Cannot assign value of type '{value_type}' to variable '{var_name}' of type '{var_type}'")
            return None
        if self.v_table.lookup(var_name):
            self.v_table.set(var_name, var_type)
        else:
            self.v_table.bind(var_name, var_type)
        return var_type

    def visit_TaskDecl(self, node: ast.TaskDecl) -> Optional[str]:
        # TODO: Check that the body of the function is type correct, and that it returns the correct type if it has a return type annotation
        # No idea how to implemnet ftable
        return None

    # General Statements ----------------------------------------

    def visit_Print(self, node: ast.Print) -> Optional[str]:
        return node.expression.accept(self)

    def visit_IfElse(self, node: ast.IfElse) -> Optional[str]:
        condition_type = node.condition.accept(self)
        if condition_type != "bool":
            print(f"Type error: Condition in if statement must be of type 'bool', got '{condition_type}'")
            return None

        saved = self.v_table
        self.v_table = self.v_table.new_scope() # New scope for then branch
        node.then_branch.accept(self)
        self.v_table = saved # Exit then branch scope

        if node.else_branch:
            saved = self.v_table
            self.v_table = self.v_table.new_scope() # New scope for else branch
            node.else_branch.accept(self)
            self.v_table = saved # Exit else branch scope
        return None

    def visit_Fallback(self, node: ast.Fallback) -> Optional[str]:
        node.primary_stmt.accept(self)
        node.fallback_stmt.accept(self)
        return None

    # Expressions ----------------------------------------

    def visit_BinaryOp(self, node: ast.BinaryOp) -> Optional[str]:
        left_type = node.left.accept(self)
        right_type = node.right.accept(self)
        op = node.operator
        # What if you say "true + true"?
        # It would fall through the match/case and then return left_type, but we disallow bool+bool
        match op:
            case "plus":
                if left_type == "int" and right_type == "int":
                    return "int"
                elif left_type == "string" and right_type == "string":
                    return "string"
            case "eq":
                if left_type == right_type:
                    return "bool"
            case "less_than":
                if left_type == "int" and right_type == "int":
                    return "bool"
            case _:
                print(f"Type error: Unsupported operator '{op}' for types '{left_type}' and '{right_type}'")
                return None

        if left_type == right_type:
            return left_type
        else:
            print(f"Type error: Cannot apply operator '{node.operator}' to types '{left_type}' and '{right_type}'")
            return None

    # Literals and Identifiers ----------------------------------------

    def visit_NullLiteral(self, node: ast.NullLiteral) -> Optional[str]:
        return "null"
    
    def visit_BooleanLiteral(self, node: ast.BooleanLiteral) -> Optional[str]:
        return "bool"
    
    def visit_NumberLiteral(self, node: ast.NumberLiteral) -> Optional[str]:
        return "int"
    
    def visit_StringLiteral(self, node: ast.StringLiteral) -> Optional[str]:
        return "string"
    
    def visit_DecimalLiteral(self, node: ast.DecimalLiteral) -> Optional[str]:
        return "decimal"
    
    def visit_ListLiteral(self, node: ast.ListLiteral) -> Optional[str]:
        if len(node.elements) == 0:
            return "list<unknown>"
        element_type = node.elements[0].accept(self)
        for elem in node.elements[1:]:
            if elem.accept(self) != element_type:
                print("Type error: List elements must all be of the same type")
                return None
        return f"list<{element_type}>"
    
    def visit_Identifier(self, node: ast.Identifier) -> Optional[str]:
        var_name = node.name
        var_type = self.v_table.lookup(var_name)
        if var_type is None:
            print(f"Type error: Undefined variable '{var_name}'")
        return var_type