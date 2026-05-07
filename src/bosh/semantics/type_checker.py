from typing import Any, Optional
import bosh.abstract_syntax.ast_nodes as ast
from .symbol_table import SymbolTable
from .ScopeStack import ScopeStack
from ..error_handler import ErrorHandler, TypeCheckError
from .FuncTable import FuncTable, FunctionSignature

class TypeChecker:
    def __init__(self):
        self.v_table = ScopeStack[str]()
        self.f_table = FuncTable()
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
        var_name = node.target
        value_type = node.value.accept(self)

        if value_type is not None:
            try:
                self.v_table.bind(var_name, value_type)
            except Exception as e:
                print(f"Type error: {e}")
                return 
        

    def visit_AssignType(self, node: ast.AssignType) -> Optional[str]:
        # Checks that the assigned value matches the declared type, and registers the variable with that type
        var_name = node.target.name
        var_type = node.var_type
        value_type = node.value.accept(self)
        if value_type and value_type != var_type:
            self.error_handler.report_error(
                message=f"Cannot assign value of type '{value_type}' to variable '{var_name}' of type '{var_type}'",
                error_type=TypeCheckError,
                node=node,
                details={"expected": var_type, "actual": value_type},
            )
            return
        try:
            self.v_table.bind(var_name, var_type)
            return
        except Exception as e:
            self.error_handler.report_error(
                message=str(e),
                error_type=TypeCheckError,
                node=node,
            )
            return
        
    def visit_TaskDecl(self, node: ast.TaskDecl) -> Optional[str]:
        #TODO complete
        param_types = ["any"] * len(node.parameters)
        signature = FunctionSignature(param_types=param_types, return_type="any")
        try:
            self.f_table.bind(node.name, signature)
        except Exception as e:
            self.error_handler.report_error(
                message=f"Task '{node.name}' is already defined.",
                error_type=TypeCheckError,
                node=node,
            )
        self.v_table.new_scope() # New scope for task body
        try:
            for param in node.parameters:
                self.v_table.bind(param, "any")
            # Return type
            body_type = node.body.accept(self)
            # Copilot autocomplete, tror det virker?
            signature.return_type = body_type if body_type else "any"
        
        finally:
            self.v_table.exit_scope()
        
        # return "task"?
        return None

# General Statements ----------------------------------------

    def visit_Print(self, node: ast.Print) -> Optional[str]:
        # value = node.expression.accept(self)
        return None

    def visit_IfElse(self, node: ast.IfElse) -> Optional[str]:
        condition_type = node.condition.accept(self)
        if condition_type != "boolean":
            self.error_handler.report_error(
                message=f"Condition in if statement must be of type 'boolean', got '{condition_type}'",
                error_type=TypeCheckError,
                node=node,
                details={"condition_type": condition_type},
            )
            return None

        self.v_table.new_scope() # New scope for then branch
        node.then_branch.accept(self)
        self.v_table.exit_scope() # Exit then branch scope

        if node.else_branch:
            self.v_table.new_scope() # New scope for else branch
            node.else_branch.accept(self)
            self.v_table.exit_scope() # Exit else branch scope
        return None

    def visit_Fallback(self, node: ast.Fallback) -> Optional[str]:
        node.primary_stmt.accept(self)
        node.fallback_stmt.accept(self)
        return None
    
    def visit_ForAll(self, node: ast.ForAll) -> Optional[str]:
        iterable_type = node.iterable.accept(self)
        if iterable_type is None:
            return None
        if not iterable_type.startswith("list<") and iterable_type.endswith(">"):
            self.error_handler.report_error(
                message=f"Iterable in for all statement must be of type 'list', got '{iterable_type}'",
                error_type=TypeCheckError,
                node=node,
                details={"iterable_type": iterable_type},
            )
            return None
        # Extract element type
        element_type = iterable_type[5:-1]  # Extract type between "list<" and ">"

        # Scoping
        self.v_table.new_scope()
        try:
            self.v_table.bind(node.iterator_name, element_type)
            node.body.accept(self)
        except Exception as e:
            self.error_handler.report_error(
                message=str(e),
                error_type=TypeCheckError,
                node=node,
            )
        finally:
            self.v_table.exit_scope()

        return None

    def visit_RepeatUntil(self, node: ast.RepeatUntil) -> Optional[str]:
        condition_type = node.condition.accept(self)
        if condition_type != "boolean":
            self.error_handler.report_error(
                message=f"Condition in repeat until statement must be of type 'boolean', got '{condition_type}'",
                error_type=TypeCheckError,
                node=node,
                details={"condition_type": condition_type},
            )
        node.body.accept(self)
        return None
    
    def visit_Quit(self, node: ast.Quit) -> Optional[str]:
        return None
    
    def visit_ListAdd(self, node: ast.ListAdd) -> Optional[str]:
        target_type = node.target.accept(self)
        node.item.accept(self) 

        if target_type != "list" and target_type != "any":
            self.error_handler.report_error(
                message=f"Cannot add to type '{target_type}'. Can only add to lists.",
                error_type=TypeCheckError,
                node=node
            )
        
        return None

    def visit_ListRemove(self, node: ast.ListRemove) -> Optional[str]:
        target_type = node.target.accept(self)
        node.item.accept(self)

        if target_type != "list" and target_type != "any":
            self.error_handler.report_error(
                message=f"Cannot remove from type '{target_type}'. Can only remove from lists.",
                error_type=TypeCheckError,
                node=node
            )
        return None
    
    def visit_Return(self, node: ast.Return) -> Optional[str]:
        return_type = node.expression.accept(self)
        return return_type
    
# Domain Statements ----------------------------------------
        
    def visit_GoTo(self, node: ast.Goto) -> Optional[str]:
        path_type = node.path.accept(self)

        if path_type not in ["text", "folder"]:
            self.error_handler.report_error(
                message=f"Path in go to statement must be of type 'text' or 'folder', got '{path_type}'",
                error_type=TypeCheckError,
                node=node
            )
        return None
    
    def visit_Make(self, node: ast.Make) -> Optional[str]:
        if node.entity_type not in ["file", "folder"]:
             self.error_handler.report_error(
                message=f"Entity type in make statement must be of type 'file' or 'folder', got '{node.entity_type}'",
                error_type=TypeCheckError,
                node=node
            )
        location_type = node.location.accept(self)
        if location_type not in ["text", "folder"]:
            self.error_handler.report_error(
                message=f"Path in make statement must be of type 'text' or 'folder', got '{location_type}'",
                error_type=TypeCheckError,
                node=node
            )
        self.v_table.bind(node.name, node.entity_type)
             
        return None
    
    def visit_Delete(self, node: ast.Delete) -> Optional[str]:
        target_type = node.target.accept(self)
        if target_type not in ["file", "folder", "text"]:
            self.error_handler.report_error(
                message=f"Cannot delete type '{target_type}'. Expected file, folder, or text.",
                error_type=TypeCheckError,
                node=node
            )
        return None
    
    def visit_Rename(self, node: ast.Rename) -> Optional[str]:
        target_type = node.target.accept(self)

        if target_type not in ["file", "folder", "text"]:
            self.error_handler.report_error(
                message=f"Cannot rename type '{target_type}'. Expected file, folder, or text.",
                error_type=TypeCheckError,
                node=node
            )
        self.v_table.bind(node.new_name, target_type)
        return None

    def visit_Copy(self, node: ast.Copy) -> Optional[str]:
        source_type = node.source.accept(self)
        target_type = node.target.accept(self)

        if source_type not in ["file", "folder", "text"]:
            self.error_handler.report_error(
                message=f"Cannot copy type '{source_type}'. Expected file, folder, or text.",
                error_type=TypeCheckError,
                node=node
            )

        if target_type not in ["folder", "text"]:
            self.error_handler.report_error(
                message=f"Target location in copy statement must be of type 'text' or 'folder', got '{target_type}'",
                error_type=TypeCheckError,
                node=node.target
            )
        return None
    
    def visit_Move(self, node: ast.Move) -> Optional[str]:
        source_type = node.source.accept(self)
        target_type = node.target.accept(self)

        if source_type not in ["file", "folder", "text"]:
            self.error_handler.report_error(
                message=f"Cannot move type '{source_type}'. Expected file, folder, or text.",
                error_type=TypeCheckError,
                node=node
            )
        if target_type not in ["folder", "text"]:
            self.error_handler.report_error(
                message=f"Target location in move statement must be of type 'text' or 'folder', got '{target_type}'",
                error_type=TypeCheckError,
                node=node.target
            )
        return None
    
    def visit_Read(self, node: ast.Read) -> Optional[str]:
        source_type = node.source.accept(self)

        if source_type not in ["file", "text"]:
            self.error_handler.report_error(
                message=f"Cannot read type '{source_type}'. Expected file or text.",
                error_type=TypeCheckError,
                node=node
            )
    
        self.v_table.bind(node.target_name, node.target_type)
        return None
    
    def visit_Write(self, node: ast.Write) -> Optional[str]:
        target_type = node.target.accept(self)
        node.content.accept(self)

        if target_type not in ["file", "text"]:
            self.error_handler.report_error(
                message=f"Cannot write to type '{target_type}'. Expected file or text.",
                error_type=TypeCheckError,
                node=node
            )
        return None

# Literals and Identifiers ----------------------------------------

    def visit_NumberLiteral(self, node: ast.NumberLiteral) -> Optional[str]:
        return "number"
    
    def visit_DecimalLiteral(self, node: ast.DecimalLiteral) -> Optional[str]:
        return "decimal"
    
    def visit_StringLiteral(self, node: ast.StringLiteral) -> Optional[str]:
        return "string"

    def visit_InterpolatedString(self, node: ast.InterpolatedString) -> Optional[str]:
        return "string"
    
    def visit_BooleanLiteral(self, node: ast.BooleanLiteral) -> Optional[str]:
        return "boolean"
    
    def visit_NullLiteral(self, node: ast.NullLiteral) -> Optional[str]:
        return "null"
    
    def visit_ListLiteral(self, node: ast.ListLiteral) -> Optional[str]:
        if len(node.elements) == 0:
            return "list<any>"
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
        try:
            var_type = self.v_table.lookup(var_name)
        except Exception as e:
            self.error_handler.report_error(
                message=f"Undefined variable '{var_name}'",
                error_type=TypeCheckError,
                node=node,
                details={"name": var_name},
            )
        return var_type
    
    def visit_TaskIdentifier(self, node: ast.TaskIdentifier) -> Optional[str]:
        try:
            self.f_table.lookup(node.name)
            return "task"
        except Exception as e:
            self.error_handler.report_error(
                message=f"Undefined task '{node.name}'",
                error_type=TypeCheckError,
                node=node,
                details={"name": node.name},
            )
        return var_type

# Expressions ----------------------------------------

    def visit_TaskCall(self, node: ast.TaskCall) -> Optional[str]:
        try:
            signature = self.f_table.lookup(node.name)
        except Exception as e:
            self.error_handler.report_error(
                message=f"Undefined task '{node.name}'",
                error_type=TypeCheckError,
                node=node,
                details={"name": node.name},
            )

        # Check amount of arguments
        if len(node.arguments) != len(signature.param_types):
            self.error_handler.report_error(
                message=f"Task '{node.name}' expects {len(signature.param_types)} arguments, but {len(node.arguments)} were provided.",
                error_type=TypeCheckError,
                node=node
            )

        # Check argument types
        for i, arg in enumerate(node.arguments):
            if i < len(signature.param_types): 
                arg_type = arg.accept(self)
                expected_type = signature.param_types[i]
                if arg_type != expected_type:
                    self.error_handler.report_error(
                        message=f"Argument {i+1} of task '{node.name}' expects type '{expected_type}', but got '{arg_type}'.",
                        error_type=TypeCheckError,
                        node=node,
                        details={"argument_index": i, "expected": expected_type, "actual": arg_type},
                    )

        return None
    
    def visit_ListLookup(self, node: ast.ListLookup) -> Optional[str]:
        target_type = node.target.accept(self)
        index_type = node.index.accept(self)

        if target_type != "list":
            self.error_handler.report_error(
                message=f"Cannot index type '{target_type}'. Expected a list.",
                error_type=TypeCheckError,
                node=node,
                details={"target_type": target_type},
            )

        if index_type != "number":
            self.error_handler.report_error(
                message=f"List index must be of type 'number', got '{index_type}'",
                error_type=TypeCheckError,
                node=node,
                details={"index_type": index_type},
            )
        return None

    def visit_BinaryOp(self, node: ast.BinaryOp) -> Optional[str]:
        left_type = node.left.accept(self)
        right_type = node.right.accept(self)
        op = node.operator
        
        if op in ["plus", "minus", "div", "mult", "mod"]:
            if left_type in ["int", "decimal"] and right_type in ["int", "decimal"]:
                return left_type
            else:
                self.error_handler.report_error(
                    message=f"Operator '{op}' not supported for types '{left_type}' and '{right_type}'",
                    error_type=TypeCheckError,
                    node=node,
                    details={"left_type": left_type, "right_type": right_type},
                )
                return None
        #TODO Finish
        elif op in ["eq", "neq"]:
            pass
        elif op in ["or", "and"]:
            pass
        elif op in ["lt", "gt", "gte", "lte"]:
            pass
        else:
            self.error_handler.report_error(
                message=f"Unsupported operator '{op}'",
                error_type=TypeCheckError,
                node=node,
                details={"operator": op},
            )
            return None
    
    def visit_UnaryOp(self, node: ast.UnaryOp) -> Optional[str]:
        operand_type = node.operand.accept(self)
        op = node.operator

        # negativ mangler i grammaren?
        if op == "-":
            if operand_type not in ["number", "decimal"]:
                self.error_handler.report_error(
                    message=f"Unary operator '{op}' not supported for type '{operand_type}'. Expected 'number' or 'decimal'.",
                    error_type=TypeCheckError,
                    node=node,
                    details={"operand_type": operand_type},
                )
                return None
        elif op == "not":
            if operand_type != "boolean":
                self.error_handler.report_error(
                    message=f"Unary operator '{op}' not supported for type '{operand_type}'. Expected 'boolean'.",
                    error_type=TypeCheckError,
                    node=node,
                    details={"operand_type": operand_type},
                )
                return None
        return None
    
    def visit_AccessOp(self, node: ast.AccessOp) -> Optional[str]:
        pass