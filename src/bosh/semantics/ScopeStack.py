from typing import Optional, Dict, List, TypeVar, Generic
from .symbol_table import SymbolTable
T = TypeVar('T')

class ScopeStack(Generic[T]):
    def __init__(self,  table: Optional[SymbolTable[T]] = SymbolTable[T](persistent=True)):
        self.table = table

    def new_scope(self, persistent: bool = True):
        self.table = self.table.new_scope(persistent=persistent)

    def exit_scope(self):
        try:
            self.table = self.table.exit_scope()
        except Exception as e:
            raise Exception("Cannot exit global scope.")
        
    
    

    def bind(self, name: str, value: T):
        try:    
            self.table.bind(name, value)
        except Exception as e:
            raise Exception(e)

    def lookup(self, name: str) -> Optional[T]:
        try:
            return self.table.lookup(name)
        except Exception as e:
            raise Exception(f"Variable '{name}' not found in any scope.")
        
    def domain(self) -> List[str]:
        return self.table.domain()


