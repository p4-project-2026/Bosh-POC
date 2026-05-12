from typing import Dict, Generic, Optional, TypeVar

T = TypeVar('T')

class Table(Generic[T]):
    def __init__(self, function_scope: bool = False, table: Optional[Dict[str, T]] = None):
        self.table: Dict[str, T] = {} if table is None else table.copy()
        self.function_scope: bool = function_scope

    def bind(self, name: str, value: T):
        if name in self.table:
            raise Exception(f"Name '{name}' already defined in scope.")
        self.table[name] = value
    
    def lookup(self, name: str) -> T:
        if name in self.table:
            return self.table[name]
        raise Exception(f"Name '{name}' not found in scope.")
    
    def contains(self, name: str) -> bool:
        return name in self.table
    
    def domain(self) -> list[str]:
        return list(self.table.keys())
    
    def get_snapshot(self) -> Dict[str, T]:
        return self.table.copy()
    
    def copy(self, function_scope: Optional[bool] = None):
        return self.__class__(
            function_scope=self.function_scope if function_scope is None else function_scope,
            table=self.get_snapshot()
        )