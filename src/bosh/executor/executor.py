from platform import node
from ..error_handler import BoshRuntimeError, RuntimeError
from .environment import Environment
from bosh.abstract_syntax import *
class Executor:
    # __init__
    def __init__(self):
        self.environment = Environment()

    # evaluate
    def execute(self, node: Program):
        try:
            node.execute(self.environment)
        except BoshRuntimeError as e:
            self.error_handler.report_error(
                message=e.message,
                error_type=RuntimeError,
                node=e.node
            )
        return None
    
"""
class Executor:
    # __init__
    def __init__(self):
        self.environment = Environment()

    # evaluate
    def evaluate(self, node: ASTNode):
        return node.accept(self)

    def general_visit(self, node: ASTNode):
        print(f"Type executor not implemented for node type: {type(node).__name__}")
        return None

    def visit_Program(self, node: Program):
        return node.block.accept(self)

    def visit_Block(self, node: Block):
        for stmt in node.statements:
            stmt.accept(self)
        return None
    # Definitions ----------------------------------------

    def visit_Assign(self, node: Assign):
        #TODO: Implement variable assignment
        return None
    
    def visit_AssignType(self, node: AssignType):
        #TODO: Implement type assignment
        return None
    
    def visit_TaskDecl(self, node: TaskDecl):
        #TODO: Implement task declaration
        return None

    # General Statements----------------------------------------

    def visit_Print(self, node: Print):
        value = node.expression.accept(self)
        print(value)
        return None
    
    def visit_IfElse(self, node: IfElse):
        condition_value = node.condition.accept(self)
        if condition_value:
            return node.if_branch.accept(self)
        elif node.else_branch:
            return node.else_branch.accept(self)
        return None
    
    def visit_Fallback(self, node: Fallback):
        try:
            return node.primary_stmt.accept(self)
        except Exception as e:
            print(f"Primary statement failed with error: {e}. Executing fallback statement.")
            return node.fallback_stmt.accept(self)

    def visit_ForAll(self, node: ForAll):
        #TODO: Implement ForAll statement
        return None
    
    def visit_RepeatUntil(self, node: RepeatUntil):
        #TODO: Implement RepeatUntil statement
        return None
    
    def visit_Quit(self, node: Quit):
        exit(0)
    
    def visit_ListAdd(self, node: ListAdd):
        #TODO: Implement ListAdd statement
        return None

    def visit_ListRemove(self, node: ListRemove):
        #TODO: Implement ListRemove statement
        return None
    
    def visit_Return(self, node: Return):
        #TODO: Implement return statement
        return None

# Domain Statements ----------------------------------------
        
    def visit_GoTo(self, node: Goto):
        #TODO: Implement GoTo statement
        return None
    
    def visit_Make(self, node: Make):
        #TODO: Implement Make statement
        return None
    
    def visit_Delete(self, node: Delete):
        #TODO: Implement Delete statement
        return None
    
    def visit_Rename(self, node: Rename):
        #TODO: Implement Rename statement
        return None

    def visit_Copy(self, node: Copy):
        #TODO: Implement Copy statement
        return None
    
    def visit_Move(self, node: Move):
        #TODO: Implement Move statement
        return None
    
    def visit_Read(self, node: Read):
        #TODO: Implement Read statement
        return None
    
    def visit_Write(self, node: Write):
        #TODO: Implement Write statement
        return None

# Literals and Identifiers ----------------------------------------    
    
    def visit_NumberLiteral(self, node: NumberLiteral):
        return node.value
    
    def visit_DecimalLiteral(self, node: DecimalLiteral):
        return node.value
    
    def visit_StringLiteral(self, node: StringLiteral):
        return node.value

    # def visit_InterpolatedString(self, node: InterpolatedString):
    #     #TODO: Implement interpolated string evaluation
    #     return None
    
    def visit_BooleanLiteral(self, node: BooleanLiteral):
        return node.value

    def visit_NullLiteral(self, node: NullLiteral):
        return None
    
    def visit_ListLiteral(self, node: ListLiteral):
        #TODO: Implement list literals
        return None

    def visit_Identifier(self, node: Identifier):
        #TODO: Implement identifier lookup
        return None

    def visit_TaskIdentifier(self, node: TaskIdentifier):
        #TODO: Implement task identifier lookup
        return None

# Expressions ----------------------------------------

    def visit_TaskCall(self, node: TaskCall):
        #TODO: Implement task call evaluation
        return None
    
    def visit_ListLookup(self, node: ListLookup):
        #TODO: Implement list lookup evaluation
        return None
    
    def visit_BinaryOp(self, node: BinaryOp):
        left_value = node.left.accept(self)
        right_value = node.right.accept(self)
        if node.operator == 'plus':
            return left_value + right_value
        elif node.operator == 'minus':
            return left_value - right_value
        elif node.operator == 'mult':
            return left_value * right_value
        elif node.operator == 'div':
            return left_value / right_value
        elif node.operator == 'eq':
            return left_value == right_value
        elif node.operator == 'neq':
            return left_value != right_value
        elif node.operator == 'gt':
            return left_value > right_value
        elif node.operator == 'lt':
            return left_value < right_value
        elif node.operator == 'gte':
            return left_value >= right_value
        elif node.operator == 'lte':
            return left_value <= right_value
        elif node.operator == 'and_':
            return left_value and right_value
        elif node.operator == 'or_':
            return left_value or right_value
        elif node.operator == 'mod':
            return left_value % right_value
        else:
            raise ValueError(f"Unsupported binary operator: {node.operator}")

    def visit_UnaryOp(self, node: UnaryOp):
        #TODO: Implement unary operation evaluation
        operand_value = node.operand.accept(self)
        if node.operator == '-':
            return -operand_value
        elif node.operator == '!':
            return not operand_value
        else:
            raise ValueError(f"Unsupported unary operator: {node.operator}")
        
"""