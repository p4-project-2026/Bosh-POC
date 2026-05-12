from typing import Any, Optional
from bosh.abstract_syntax import *
from xmlrpc.client import boolean
import bosh.abstract_syntax.ast_nodes as ast
from .symbol_table import SymbolTable
from .ScopeStack import ScopeStack
from ..error_handler import ErrorHandler, TypeCheckError, BoshTypeError, BoshRuntimeError
from .FuncTable import FuncTable, FunctionSignature

class TypeChecker:
    def __init__(self):
        self.v_table = ScopeStack[str]()
        self.f_table = FuncTable()
        self.error_handler = ErrorHandler()

    def check(self, program_ast: Program):
        try:
            program_ast.check(self.v_table, self.f_table)
        except BoshTypeError as e:
            self.error_handler.report_error(
                message=e.message,
                error_type=TypeCheckError,
                node=e.node
            )
    

    def default_visit(self, node: ASTNode) -> Optional[str]:
        self.error_handler.report_error(
            message=f"Type checking not implemented for node type: {type(node).__name__}",
            error_type=TypeCheckError,
            node=node,
        )
        return None

    def visit_Program(self, node: Program) -> Optional[str]:
        return node.block.accept(self)

    def visit_Block(self, node: Block) -> Optional[str]:
        for stmt in node.statements:
            stmt.accept(self)
        return None

# Definitions ----------------------------------------

    def visit_Assign(self, node: Assign) -> Optional[str]:
        var_name = node.target.name
        value_type = node.value.accept(self)

        if value_type is not None:
            try:
                self.v_table.bind(var_name, value_type)
            except Exception as e:
                print(f"Type error: {e}")
                return 
        

    def visit_AssignType(self, node: AssignType) -> Optional[str]:
        # Checks that the assigned value matches the declared type, and registers the variable with that type
        var_name = node.target
        var_type = node.var_type
        value_type = node.value.accept(self)
        if var_type == "list" and isinstance(value_type, str) and value_type.startswith("list"):
            var_type = value_type  # If variable is declared as list, take the element type from the assigned value
        elif value_type != var_type:
            self.error_handler.report_error(
                message=f"Cannot assign value of type '{value_type}' to variable '{var_name}' of type '{var_type}'",
                error_type=TypeCheckError,
                node=node,
                details={"expected": var_type, "actual": value_type},
            )
            return None
        
        self.v_table.bind(var_name, var_type)
        return None
        
    def visit_TaskDecl(self, node: ast.TaskDecl) -> Optional[str]:
        parameters = {param: "any" for param in node.parameters}
        signature = FunctionSignature(parameters=parameters)
        try:
            self.f_table.bind(node.name, signature)
        except Exception as e:
            self.error_handler.report_error(
                message=f"Task '{node.name}' is already defined.",
                error_type=TypeCheckError,
                node=node,
            )
        self.v_table.new_scope()
        try:
            for param in node.parameters:
                self.v_table.bind(param, "any")
            # Return type
            node.body.accept(self)
        
        finally:
            self.v_table.exit_scope()
        
        return None

# General Statements ----------------------------------------

    def visit_Print(self, node: Print) -> Optional[str]:
        # value = node.expression.accept(self)
        return None

    def visit_IfElse(self, node: IfElse) -> Optional[str]:
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

    def visit_Fallback(self, node: Fallback) -> Optional[str]:
        node.primary_stmt.accept(self)
        node.fallback_stmt.accept(self)
        return None
    
    def visit_ForAll(self, node: ForAll) -> Optional[str]:
        iterable_type = node.iterable.accept(self)
        if iterable_type is None:
            return None
        if not isinstance(iterable_type, str) or not iterable_type.startswith("list"):
            self.error_handler.report_error(
                message=f"Type error: Cannot iterate over type '{iterable_type}'. Expected a list.",
                error_type=TypeCheckError,
                node=node
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

    def visit_RepeatUntil(self, node: RepeatUntil) -> Optional[str]:
        condition_type = node.condition.accept(self)
        if condition_type != "boolean":
            self.error_handler.report_error(
                message=f"Condition in repeat until statement must be of type 'boolean', got '{condition_type}'",
                error_type=TypeCheckError,
                node=node,
                details={"condition_type": condition_type},
            )
        self.v_table.new_scope()
        try:
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
    
    def visit_Quit(self, node: Quit) -> Optional[str]:
        return None
    
    def visit_ListAdd(self, node: ListAdd) -> Optional[str]:
        target_type = node.target.accept(self)
        item_type = node.item.accept(self) 

        if not isinstance(target_type, str) or not target_type.startswith("list"):
            self.error_handler.report_error(
                message=f"Cannot add to type '{target_type}'. Can only add to lists.",
                error_type=TypeCheckError,
                node=node
            )
            return None

        if "<" in target_type and ">" in target_type:
            expected_type = target_type[5:-1]  # Extract type between "list<" and ">"

            if item_type != expected_type and expected_type != "any":
                self.error_handler.report_error(
                    message=f"Cannot add item of type '{item_type}' to list of '{expected_type}'",
                    error_type=TypeCheckError,
                    node=node,
                    details={"item_type": item_type, "expected_type": expected_type},
                )
            return None
        
        return None

    def visit_ListRemove(self, node: ListRemove) -> Optional[str]:
        target_type = node.target.accept(self)
        item_type = node.item.accept(self)

        if not isinstance(target_type, str) or not target_type.startswith("list"):
            self.error_handler.report_error(
                message=f"Cannot remove from type '{target_type}'. Can only remove from lists.",
                error_type=TypeCheckError,
                node=node
            )
            return None
    
        if "<" in target_type and ">" in target_type:
            expected_type = target_type[5:-1]  # Extract type between "list<" and ">"

            if item_type != expected_type and expected_type != "any":
                self.error_handler.report_error(
                    message=f"Cannot remove item of type '{item_type}' from list of '{expected_type}'",
                    error_type=TypeCheckError,
                    node=node,
                    details={"item_type": item_type, "expected_type": expected_type},
                )
            return None
        
        return None
    
    def visit_Return(self, node: ast.Return) -> Optional[str]:
        return_type = node.expression.accept(self)
        return return_type
    
# Domain Statements ----------------------------------------
        #TODO test!!!
    def visit_GoTo(self, node: ast.Goto) -> Optional[str]:
        path_type = node.path.accept(self)

        if path_type not in ["text", "folder"]:
            self.error_handler.report_error(
                message=f"Path in 'go to' statement must be of type 'text' or 'folder', got '{path_type}'",
                error_type=TypeCheckError,
                node=node
            )
        return None
    
    def visit_Make(self, node: ast.Make) -> Optional[str]:
        name_type = node.name.accept(self)
        if name_type is not None and name_type != "text":
            self.error_handler.report_error(
                message=f"Cannot use type '{name_type}' as a new name. Expected 'text'.",
                error_type=TypeCheckError, 
                node=node
            )

        if node.entity_type not in ["file", "folder"]:
             self.error_handler.report_error(
                message=f"Entity type in make statement must be of type 'file' or 'folder', got '{node.entity_type}'",
                error_type=TypeCheckError,
                node=node
            )
        location_type = node.location.accept(self)
        if location_type not in ["text", "folder"]:
            self.error_handler.report_error(
                message=f"Path in 'make' statement must be of type 'text' or 'folder', got '{location_type}'",
                error_type=TypeCheckError,
                node=node
            )
        return None
    
    def visit_Delete(self, node: Delete) -> Optional[str]:
        target_type = node.target.accept(self)
        if target_type not in ["file", "folder", "text"]:
            self.error_handler.report_error(
                message=f"Cannot delete type '{target_type}'. Expected file, folder, or text.",
                error_type=TypeCheckError,
                node=node
            )
        return None
    
    def visit_Rename(self, node: Rename) -> Optional[str]:
        target_type = node.target.accept(self)
        new_name_type = node.new_name.accept(self)

        if target_type not in ["file", "folder", "text"]:
            self.error_handler.report_error(
                message=f"Cannot rename type '{target_type}'. Expected file, folder, or text.",
                error_type=TypeCheckError,
                node=node
            )
        if new_name_type not in ["text", "file", "folder"]:
            self.error_handler.report_error(
                message=f"Cannot use type '{new_name_type}' as a new name. Expected 'text'.",
                error_type=TypeCheckError,
                node=node
            )

        return None

    def visit_Copy(self, node: Copy) -> Optional[str]:
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
    
    def visit_GoUp(self, node: ast.GoUp) -> Optional[str]:
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
    
    def visit_Read(self, node: Read) -> Optional[str]:
        source_type = node.source.accept(self)

        if source_type not in ["file", "text"]:
            self.error_handler.report_error(
                message=f"Cannot read type '{source_type}'. Expected file or text.",
                error_type=TypeCheckError,
                node=node
            )
    
        return None
    
    def visit_Write(self, node: Write) -> Optional[str]:
        target_type = node.target.accept(self)
        data_type = node.data.accept(self)

        if target_type not in ["file", "text"]:
            self.error_handler.report_error(
                message=f"Cannot write to type '{target_type}'. Expected file or text.",
                error_type=TypeCheckError,
                node=node
            )
        if data_type != "text":
            self.error_handler.report_error(
                message=f"Data in write statement must be of type 'text', got '{data_type}'",
                error_type=TypeCheckError,
                node=node
            )
        return None

    def visit_Execute(self, node: ast.Execute) -> Optional[str]:
        target_type = node.target.accept(self)
        if target_type not in ["file", "text"]:
            self.error_handler.report_error(
                message=f"Cannot execute type '{target_type}'. Expected file or path.",
                error_type=TypeCheckError,
                node=node
            )
        return None
    
    def visit_Pause(self, node: ast.Pause) -> Optional[str]:
        return None
    
    def visit_Wait(self, node: ast.Wait) -> Optional[str]:
        duration_type = node.time.accept(self)
        if duration_type not in ["number", "decimal", "time"]:
            self.error_handler.report_error(
                message=f"Duration in 'wait' must be of type 'number', 'decimal' or 'time', got '{duration_type}'",
                error_type=TypeCheckError,
                node=node,
            )
        return None


# Literals and Identifiers ----------------------------------------

    def visit_NumberLiteral(self, node: NumberLiteral) -> Optional[str]:
        return "number"
    
    def visit_DecimalLiteral(self, node: DecimalLiteral) -> Optional[str]:
        return "decimal"
    
    def visit_StringLiteral(self, node: ast.StringLiteral) -> Optional[str]:
        return "text"

    def visit_InterpolatedString(self, node: ast.InterpolatedString) -> Optional[str]:
        return "text"
    
    def visit_BooleanLiteral(self, node: BooleanLiteral) -> Optional[str]:
        return "boolean"
    
    def visit_NullLiteral(self, node: NullLiteral) -> Optional[str]:
        return "null"
    
    def visit_ListLiteral(self, node: ListLiteral) -> Optional[str]:
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
    
    def visit_DateLiteral(self, node: ast.DateLiteral) -> Optional[str]:
        return "date"

    def visit_TimeLiteral(self, node: ast.TimeLiteral) -> Optional[str]:
        return "time"

    def visit_FolderLiteral(self, node: ast.FolderLiteral) -> Optional[str]:
        return "folder"

    def visit_FileLiteral(self, node: ast.FileLiteral) -> Optional[str]:
        return "file"
    
    def visit_Input(self, node: ast.Input) -> Optional[str]:
            prompt_type = node.prompt.accept(self) if node.prompt else None
            if prompt_type != "text":
                self.error_handler.report_error(
                    message=f"Prompt in input statement must be of type 'text', got '{prompt_type}'",
                    error_type=TypeCheckError,
                    node=node,
                    details={"prompt_type": prompt_type},
                )
                return None
            return "text"
    
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
    
    def visit_TaskIdentifier(self, node: TaskIdentifier) -> Optional[str]:
        try:
            signature = self.f_table.lookup(node.name)
        except Exception as e:
            self.error_handler.report_error(
                message=f"Undefined task '{node.name}'",
                error_type=TypeCheckError,
                node=node,
                details={"name": node.name},
            )
            return None
        provided_args = getattr(node, 'args', getattr(node, 'arguments', []))
        expected_args = signature.param

        if len(provided_args) != len(expected_args):
            self.error_handler.report_error(
                message=f"Task '{node.name}' expects {len(expected_args)} arguments, but {len(provided_args)} were provided.",
                error_type=TypeCheckError,
                node=node,
                details={"expected_arg_count": len(expected_args), "provided_arg_count": len(provided_args)},
            )
            return None
        for arg in provided_args:
            arg.accept(self)

        return getattr(signature, "return_type", "any")

# Expressions ----------------------------------------
    def visit_TaskCall(self, node: ast.TaskCall) -> Optional[str]:
        try:
            signature = self.f_table.lookup(node.name)
            if len(signature.param) != len(node.arguments):
                self.error_handler.report_error(
                    message=f"Task '{node.name}' expects {len(signature.param)} arguments, but {len(node.arguments)} were provided.",
                    error_type=TypeCheckError,
                    node=node,
                    details={"expected_arg_count": len(signature.param), "provided_arg_count": len(node.arguments)},
                )
                return None
            for arg in node.arguments:
                arg.accept(self)
        
        except Exception as e:
            self.error_handler.report_error(
                message=f"Undefined task '{node.name}'",
                error_type=TypeCheckError,
                node=node,
                details={"name": node.name},
            )
            return None
        
        return signature.return_type
    
    def visit_ListLookup(self, node: ListLookup) -> Optional[str]:
        target_type = node.target.accept(self)
        index_type = node.index.accept(self)

        if not isinstance(target_type, str) or not target_type.startswith("list"):
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

    def visit_BinaryOp(self, node: BinaryOp) -> Optional[str]:
        left_type = node.left.accept(self)
        right_type = node.right.accept(self)
        op = node.operator
        if left_type == "any" or right_type == "any":
            return "any"
        
        if op in ["plus", "minus", "div", "mult", "mod"]:
            if left_type in ["number", "decimal"] and right_type in ["number", "decimal"]:
                return "decimal" if "decimal" in [left_type, right_type] else "number"
            elif op == "plus" and left_type == "text" and right_type == "text":
                return "text"
            else:
                self.error_handler.report_error(
                    message=f"Operator '{op}' not supported for types '{left_type}' and '{right_type}'",
                    error_type=TypeCheckError,
                    node=node,
                    details={"left_type": left_type, "right_type": right_type},
                )
                return None
            
        elif op in ["eq", "neq"]:
            numeric_eq = (left_type in ["number", "decimal"] and right_type in ["number", "decimal"])
            null_eq = (left_type == "null" or right_type == "null")
            if left_type != right_type and not numeric_eq and not null_eq:
                self.error_handler.report_error(
                    message=f"Operator '{op}' not supported for types '{left_type}' and '{right_type}'",
                    error_type=TypeCheckError,
                    node=node,
                    details={"left_type": left_type, "right_type": right_type},
                )
                return None
            return "boolean"
        
        elif op in ["or", "and"]:
            if left_type != "boolean" or right_type != "boolean":
                self.error_handler.report_error(
                    message=f"Logical operator '{op}' requires boolean operands, got '{left_type}' and '{right_type}'",
                    error_type=TypeCheckError,
                    node=node,
                    details={"left_type": left_type, "right_type": right_type},
                )
                return None
            return "boolean"
        
        elif op in ["lt", "gt", "gte", "lte"]:
            if left_type not in ["number", "decimal", "date", "time"] or right_type not in ["number", "decimal", "date", "time"]:
                self.error_handler.report_error(
                    message=f"Relational operator '{op}' requires numeric or temporal operands, got '{left_type}' and '{right_type}'.",
                    error_type=TypeCheckError,
                    node=node,
                    details={"left_type": left_type, "right_type": right_type},
                )
                return None
            return "boolean"
        
        else:
            self.error_handler.report_error(
                message=f"Unsupported operator '{op}'",
                error_type=TypeCheckError,
                node=node,
                details={"operator": op},
            )
            return None
    
    def visit_UnaryOp(self, node: UnaryOp) -> Optional[str]:
        operand_type = node.operand.accept(self)
        op = node.operator

        # negativ mangler i grammaren?
        if op in ["-", "neg", "negative"]:
            if operand_type not in ["number", "decimal"]:
                self.error_handler.report_error(
                    message=f"Unary operator '{op}' not supported for type '{operand_type}'. Expected 'number' or 'decimal'.",
                    error_type=TypeCheckError,
                    node=node,
                    details={"operand_type": operand_type},
                )
                return None
            return operand_type
        elif op in ["not_", "not", "!"]:
            if operand_type != "boolean":
                self.error_handler.report_error(
                    message=f"Unary operator '{op}' not supported for type '{operand_type}'. Expected 'boolean'.",
                    error_type=TypeCheckError,
                    node=node,
                    details={"operand_type": operand_type},
                )
                return None
            return "boolean"
        
        elif op in ["floor", "ceiling", "round"]:
            if operand_type not in ["number", "decimal"]:
                self.error_handler.report_error(
                    message=f"Unary operator '{op}' not supported for type '{operand_type}'. Expected 'number' or 'decimal'.",
                    error_type=TypeCheckError,
                    node=node,
                    details={"operand_type": operand_type},
                )
                return None
            return "number"
        
        elif op == "exponent":
            if operand_type not in ["number", "decimal"]:
                self.error_handler.report_error(
                    message=f"Unary operator 'exponent' not supported for type '{operand_type}'. Expected 'number' or 'decimal'.",
                    error_type=TypeCheckError,
                    node=node,
                    details={"operand_type": operand_type},
                )
                return None
            return "decimal"
        
        elif op == "length":
            if operand_type not in ["text", "list"]:
                self.error_handler.report_error(
                    message=f"Unary operator 'length' not supported for type '{operand_type}'. Expected 'text' or 'list'.",
                    error_type=TypeCheckError,
                    node=node,
                    details={"operand_type": operand_type},
                )
                return None
            return "number"
        
        elif op in ["first", "last"]:
            is_list = isinstance(operand_type, str) and operand_type.startswith("list")
            if operand_type != "text" and not is_list:
                self.error_handler.report_error(
                    message=f"Unary operator '{op}' not supported for type '{operand_type}'. Expected 'text' or 'list'.",
                    error_type=TypeCheckError,
                    node=node,
                    details={"operand_type": operand_type},
                )
                return None
            if operand_type == "text":
                return "text"
            else:
                return operand_type[5:-1]
            
        else:
            self.error_handler.report_error(
                message=f"Unsupported unary operator '{op}'",
                error_type=TypeCheckError,
                node=node,
                details={"operator": op},
            )
            return None
    
    def visit_AccessOp(self, node: ast.AccessOp) -> Optional[str]:
        target_type = node.target.accept(self)
        op = node.operation

        if op == "file_name":
            if target_type not in ["file", "folder"]:
                self.error_handler.report_error(
                    message=f"Cannot get file name of type '{target_type}'. Expected 'file' or 'folder'.",
                    error_type=TypeCheckError,
                    node=node,
                    details={"target_type": target_type},
                )
                return None
            return "text"
        
        elif op == "age":
            if target_type not in ["file", "folder"]:
                self.error_handler.report_error(
                    message=f"Cannot get age of type '{target_type}'. Expected 'file' or 'folder'.",
                    error_type=TypeCheckError,
                    node=node,
                    details={"target_type": target_type},
                )
                return None
            return "number"
        
        elif op in ["starts_with", "ends_with", "regex"]:
            if target_type != "text":
                self.error_handler.report_error(
                    message=f"Cannot apply operation '{op}' to type '{target_type}'. Expected 'text'.",
                    error_type=TypeCheckError,
                    node=node,
                    details={"target_type": target_type, "operation": op},
                )
                return None

            if node.argument is not None:
                arg_type = node.argument.accept(self)
                if arg_type != "text":
                    self.error_handler.report_error(
                        message=f"Argument for operation '{op}' must be of type 'text', got '{arg_type}'.",
                        error_type=TypeCheckError,
                        node=node,
                        details={"argument_type": arg_type, "operation": op},
                    )
                    return None
            return "boolean"
        
        #TODO access ops for unit, and parsing for date and time literals
        elif op == "unit":
            if target_type in ["number", "decimal"]:
                return "time"
            elif target_type == "time":
                return "number"
            
            else:
                self.error_handler.report_error(
                    message=f"Time units require a numeric, date, or time target, got '{target_type}'.",
                    error_type=TypeCheckError, node=node
                )
                return None   
        
        elif op == "now":
            return "date"
        
        elif op == "here":
            return "folder"
        
        else:
            self.error_handler.report_error(
                message=f"Unsupported access operation '{op}'",
                error_type=TypeCheckError,
                node=node,
                details={"operation": op},
            )
            return None