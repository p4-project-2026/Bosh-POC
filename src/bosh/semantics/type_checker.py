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
            case ast.Program:
                self.check(node.block)
            case ast.Block:
                for stmt in node.statements:
                    self.check(stmt)
            case ast.Assign:
                var_name = node.target.name
                value_type = self.check(node.value)
                if value_type is not None:
                    self.symbol_table[var_name] = value_type
            case ast.Print:
                self.check(node.expression)
            case ast.BinaryOp:
                left_type = self.check(node.left)
                right_type = self.check(node.right)
                if left_type == right_type:
                    return left_type
                else:
                    print(f"Type error: Cannot apply operator '{node.operation}' to types '{left_type}' and '{right_type}'")
                    return None
            case _:
                print(f"Type checking not implemented for node type: {type(node).__name__}")
                return None
