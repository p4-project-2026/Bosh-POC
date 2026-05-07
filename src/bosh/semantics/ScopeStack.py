from typing import Optional, Dict, List, TypeVar, Generic
from .symbol_table import SymbolTable
T = TypeVar('T')

class ScopeStack(Generic[T]):
    def __init__(self,  table: Optional[SymbolTable[T]] = None, write_through: bool = True):
        self.table = table if table is not None else SymbolTable[T](write_through=write_through)

    def new_scope(self, write_through: bool = True):
        self.table = self.table.new_scope(write_through=write_through)

    def exit_scope(self):
        try:
            self.table = self.table.exit_scope()
        except Exception as e:
            raise Exception("Cannot exit global scope.")
        
    def snapshot(self) -> Dict[str, T]:
        return ScopeStack(self.table.snapshot_table())
    
    
    def bind_local(self, name: str, value: T):
        try:
            self.table.bind_local(name, value)
        except Exception as e:
            raise Exception(f"Variable '{name}' already bound to a different type in local scope.")

    def bind(self, name: str, value: T):
        try:    
            self.table.bind(name, value)
        except Exception as e:
            raise Exception(f"Variable '{name}' already bound to a different type in local scope.")

    def lookup(self, name: str) -> Optional[T]:
        try:
            return self.table.lookup(name)
        except Exception as e:
            raise Exception(f"Variable '{name}' not found in any scope.")
        
    def domain(self) -> List[str]:
        return self.table.domain()