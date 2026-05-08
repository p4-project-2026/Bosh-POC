from dataclasses import dataclass

from bosh.abstract_syntax.ast_base import Block
from bosh.semantics.symbol_table import SymbolTable
from bosh.semantics.ScopeStack import ScopeStack


'''
# This was an incorrect implementation of the function table.
# It's only still here because I know we're leaving the repo.
'''


from typing import Dict, Optional, Any, TypeVar
@dataclass
class FunctionDef:
    parameters: list[str]
    the_function_parent_scope: ScopeStack
    body: Block

    def __init__(self, parameters: list[str], the_function_parent_scope: ScopeStack, body: Block):
        self.parameters = parameters
        self.the_function_parent_scope = the_function_parent_scope
        self.body = body
    


class FuncTableForExecutor(SymbolTable[FunctionDef]):
    def __init__(self, parent: Optional['FuncTableForExecutor'] = None, write_through: bool = True):
        super().__init__(parent=parent, write_through=write_through)
    
    def new_scope(self):
        raise Exception("Cannot create new scope for function definitions. Function definitions are global.")
    
    def exit_scope(self):
        raise Exception("Cannot exit scope for function definitions. Function definitions are global.")
    
    def update(self, name, type_value):
        raise Exception("Cannot update function definitions. Function definitions are global and immutable.")
    
    def bind(self, name: str, function_def: FunctionDef):
        if name in self.table:
            raise Exception(f"Function '{name}' already defined in scope.")
        self.table[name] = function_def
    
    def lookup(self, name: str) -> FunctionDef:
        if name in self.table:
            return self.table[name]
        raise Exception(f"Function '{name}' not found in scope.")
    