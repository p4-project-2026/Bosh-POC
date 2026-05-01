from dataclasses import dataclass
from platform import node
from typing import Optional, Dict
from unittest import case
import bosh.parser.ast_nodes as ast

class TypeChecker:
    def __init__(self):
        self.symbol_table: Dict[str, str] = {}  # Variabelnavn -> type

    def check(self, node: ast.ASTNode) -> Optional[str]:
        match node:
            case ast.Program():
                self.check(node.block)

            case ast.Block():
                for stmt in node.statements:
                    self.check(stmt)
            # Definitions ----------------------------------------
            case ast.Assign():
                var_name = node.target.name
                value_type = self.check(node.value)
                if value_type is not None:
                    self.symbol_table[var_name] = value_type
            
            case ast.AssignType():
                pass #What is AssignType? Is it explicit conversion or just a way to double-check?

            case ast.TaskDecl():
                pass #How to handle function declarations?
            
            # General Statements ----------------------------------------

            case ast.Print():
                self.check(node.expression)

            case ast.IfElse():
                self.check(node.condition)
                self.check(node.then_branch)
                if node.else_branch:
                    self.check(node.else_branch)
            
            case ast.Fallback():
                self.check(node.primary_stmt)
                self.check(node.fallback_stmt)

            

            

            case ast.BinaryOp():
                left_type = self.check(node.left)
                right_type = self.check(node.right)
                op = node.operator
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
                
            case ast.NullLiteral():
                return "null"
            case ast.BooleanLiteral():
                return "bool"
            case ast.NumberLiteral():
                return "int"
            case ast.StringLiteral():
                return "string"
            case ast.DecimalLiteral():
                return "decimal"
            case ast.ListLiteral():
                if len(node.elements) == 0:
                    return "list<unknown>"
                element_type = self.check(node.elements[0])
                for elem in node.elements[1:]:
                    if self.check(elem) != element_type:
                        print("Type error: List elements must all be of the same type")
                        return None
                return f"list<{element_type}>"
            
            case ast.Identifier():
                var_name = node.name
                if var_name in self.symbol_table:
                    return self.symbol_table[var_name]
                else:
                    print(f"Type error: Undefined variable '{var_name}'")
                    return None
                
        
            case _:
                print(f"Type checking not implemented for node type: {type(node).__name__}")
                return None
