from typing import Optional
import bosh.abstract_syntax.ast_nodes as ast
from .symbol_table import SymbolTable
from ..error_handler import ErrorHandler, TypeCheckError

class TypeChecker:
    def __init__(self):
        self.v_table = SymbolTable()
        self.error_handler = ErrorHandler()

    def check(self, node: ast.ASTNode) -> Optional[str]:
        return node.accept(self)

    def default_visit(self, node: ast.ASTNode) -> Optional[str]:
        self.error_handler.report_error(
            message=f"Type checking not implemented for node type: {type(node).__name__}",
            error_type=TypeCheckError,
            node=node,
        )
        return None

    def visit_Program(self, node: ast.Program) -> Optional[str]:
        return node.block.accept(self)

    def visit_Block(self, node: ast.Block) -> Optional[str]:
        for stmt in node.statements:
            stmt.accept(self)
        return None

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
            self.error_handler.report_error(
                message=f"Cannot assign value of type '{value_type}' to variable '{var_name}' of type '{var_type}'",
                error_type=TypeCheckError,
                node=node,
                details={"expected": var_type, "actual": value_type},
            )
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
            self.error_handler.report_error(
                message=f"Condition in if statement must be of type 'bool', got '{condition_type}'",
                error_type=TypeCheckError,
                node=node,
                details={"condition_type": condition_type},
            )
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
    
    def visit_ForAll(self, node: ast.ForAll) -> Optional[str]:
        #TODO: implement
        return None

    def visit_RepeatUntil(self, node: ast.RepeatUntil) -> Optional[str]:
        #TODO: implement
        return None
    
    def visit_Quit(self, node: ast.Quit) -> Optional[str]:
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
                self.error_handler.report_error(
                    message="List elements must all be of the same type",
                    error_type=TypeCheckError,
                    node=node,
                    details={"expected": element_type},
                )
                return None
        return f"list<{element_type}>"
    
    def visit_Identifier(self, node: ast.Identifier) -> Optional[str]:
        var_name = node.name
        var_type = self.v_table.lookup(var_name)
        if var_type is None:
            self.error_handler.report_error(
                message=f"Undefined variable '{var_name}'",
                error_type=TypeCheckError,
                node=node,
                details={"name": var_name},
            )
        return var_type
    
    # Expressions ----------------------------------------

    def visit_BinaryOp(self, node: ast.BinaryOp) -> Optional[str]:
        left_type = node.left.accept(self)
        right_type = node.right.accept(self)
        op = node.operator
        
        if op in ["plus", "minus"]:
            if left_type == right_type and left_type in ["int", "decimal"]:
                return left_type
            else:
                self.error_handler.report_error(
                    message=f"Operator '{op}' not supported for types '{left_type}' and '{right_type}'",
                    error_type=TypeCheckError,
                    node=node,
                    details={"left_type": left_type, "right_type": right_type},
                )
                return None
        elif op in ["mult", "div"]:
            if left_type == right_type and left_type in ["int", "decimal"]:
                return left_type
            else:
                self.error_handler.report_error(
                    message=f"Operator '{op}' not supported for types '{left_type}' and '{right_type}'",
                    error_type=TypeCheckError,
                    node=node,
                    details={"left_type": left_type, "right_type": right_type},
                )
                return None
        else:
            self.error_handler.report_error(
                message=f"Unsupported operator '{op}'",
                error_type=TypeCheckError,
                node=node,
                details={"operator": op},
            )
            return None
    