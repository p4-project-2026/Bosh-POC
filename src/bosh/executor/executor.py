from platform import node

from .environment import Environment
import bosh.parser.ast_nodes as ast

class Executor:
    # __init__
    def __init__(self):
        self.environment = Environment()

    # evaluate
    def evaluate(self, node: ast.ASTNode):
        return node.accept(self)

    def general_visit(self, node: ast.ASTNode):
        print(f"Type executor not implemented for node type: {type(node).__name__}")
        return None

    def visit_Program(self, node: ast.Program):
        return node.block.accept(self)

    def visit_Block(self, node: ast.Block):
        for stmt in node.statements:
            stmt.accept(self)
        return None
    # Definitions ----------------------------------------

    def visit_Assign(self, node: ast.Assign):
        #TODO: Implement variable assignment
        return None
    
    def visit_AssignType(self, node: ast.AssignType):
        #TODO: Implement type assignment
        return None
    
    def visit_TaskDecl(self, node: ast.TaskDecl):
        #TODO: Implement task declaration
        return None

    # General Statements----------------------------------------

    def visit_Print(self, node: ast.Print):
        value = node.expression.accept(self)
        print(value)
        return None
    
    def visit_IfElse(self, node: ast.IfElse):
        condition_value = node.condition.accept(self)
        if condition_value:
            return node.if_block.accept(self)
        elif node.else_block:
            return node.else_block.accept(self)
        return None
    
    def visit_Fallback(self, node: ast.Fallback):
        try:
            return node.primary_stmt.accept(self)
        except Exception as e:
            print(f"Primary statement failed with error: {e}. Executing fallback statement.")
            return node.fallback_stmt.accept(self)

    def visit_ForAll(self, node: ast.ForAll):
        #TODO: Implement ForAll statement
        return None
    
    def visit_RepeatUntil(self, node: ast.RepeatUntil):
        #TODO: Implement RepeatUntil statement
        return None
    
    def visit_Quit(self, node: ast.Quit):
        exit(0)
    
    def visit_ListAdd(self, node: ast.ListAdd):
        #TODO: Implement ListAdd statement
        return None

    def visit_ListRemove(self, node: ast.ListRemove):
        #TODO: Implement ListRemove statement
        return None
    
    def visit_Return(self, node: ast.Return):
        #TODO: Implement return statement
        return None

# Domain Statements ----------------------------------------
        
    def visit_GoTo(self, node: ast.Goto):
        #TODO: Implement GoTo statement
        return None
    
    def visit_Make(self, node: ast.Make):
        #TODO: Implement Make statement
        return None
    
    def visit_Delete(self, node: ast.Delete):
        #TODO: Implement Delete statement
        return None
    
    def visit_Rename(self, node: ast.Rename):
        #TODO: Implement Rename statement
        return None

    def visit_Copy(self, node: ast.Copy):
        #TODO: Implement Copy statement
        return None
    
    def visit_Move(self, node: ast.Move):
        #TODO: Implement Move statement
        return None
    
    def visit_Read(self, node: ast.Read):
        #TODO: Implement Read statement
        return None
    
    def visit_Write(self, node: ast.Write):
        #TODO: Implement Write statement
        return None

# Literals and Identifiers ----------------------------------------    
    
    def visit_NumberLiteral(self, node: ast.NumberLiteral):
        return node.value
    
    def visit_DecimalLiteral(self, node: ast.DecimalLiteral):
        return node.value
    
    def visit_StringLiteral(self, node: ast.StringLiteral):
        return node.value

    # def visit_InterpolatedString(self, node: ast.InterpolatedString):
    #     #TODO: Implement interpolated string evaluation
    #     return None
    
    def visit_BooleanLiteral(self, node: ast.BooleanLiteral):
        return node.value

    def visit_NullLiteral(self, node: ast.NullLiteral):
        return None
    
    def visit_ListLiteral(self, node: ast.ListLiteral):
        #TODO: Implement list literals
        return None

    def visit_Identifier(self, node: ast.Identifier):
        #TODO: Implement identifier lookup
        return None

    def visit_TaskIdentifier(self, node: ast.TaskIdentifier):
        #TODO: Implement task identifier lookup
        return None

# Expressions ----------------------------------------

    def visit_TaskCall(self, node: ast.TaskCall):
        #TODO: Implement task call evaluation
        return None
    
    def visit_ListLookup(self, node: ast.ListLookup):
        #TODO: Implement list lookup evaluation
        return None
    
    def visit_BinaryOp(self, node: ast.BinaryOp):
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

    def visit_UnaryOp(self, node: ast.UnaryOp):
        #TODO: Implement unary operation evaluation
        operand_value = node.operand.accept(self)
        if node.operator == '-':
            return -operand_value
        elif node.operator == '!':
            return not operand_value
        else:
            raise ValueError(f"Unsupported unary operator: {node.operator}")