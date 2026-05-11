from typing import Dict, Generic, TypeVar

T = TypeVar('T')

class Table(Generic[T]):
    def __init__(self, function_scope: bool = False):
        self.table: Dict[str, T] = {}
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