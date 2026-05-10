from typing import Optional, Dict, List, TypeVar, Generic
from .symbol_table import SymbolTable
from dataclasses import dataclass
T = TypeVar('T')

@dataclass
class FunctionSignature:
    param: List[str]
    param_types: Dict[str, str]
    return_type: Optional[str] = None
    
    def __init__(self, parameters: Dict[str, str], return_type: Optional[str] = None):
        self.param = list(parameters.keys())
        self.param_types = parameters
        self.return_type = return_type

class FuncTable(SymbolTable[FunctionSignature]):
    def __init__(self, parent: Optional['FuncTable'] = None, write_through: bool = True):
        super().__init__(parent=parent, write_through=write_through)

    def new_scope(self):
        raise Exception("Cannot create new scope for function definitions. Function definitions are global.")
    
    def exit_scope(self):
        raise Exception("Cannot exit scope for function definitions. Function definitions are global.")
    
    def update(self, name, type_value):
        raise Exception("Cannot update function definitions. Function definitions are global and immutable.")

    def bind(self, name: str, signature: FunctionSignature):
        if name in self.table:
            raise Exception(f"Function '{name}' already defined in scope.")
        self.table[name] = signature

    def lookup(self, name: str) -> FunctionSignature:
        if name in self.table:
            return self.table[name]
        raise Exception(f"Function '{name}' not found in any scope.")
    