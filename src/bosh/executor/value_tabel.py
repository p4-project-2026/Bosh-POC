from bosh.semantics.symbol_table import SymbolTable
from typing import Optional, Any, TypeVar

class ValueTable(SymbolTable[Any]):
    def __init__(self, parent: Optional['ValueTable'] = None, persistent: bool = True):
        super().__init__(parent=parent, persistent=persistent)
    
    def bind_local(self, name: str, value: Any):
        if name in self.table:
            if self.table[name] != value:
                raise Exception(f"Variable '{name}' already bound to a different type in local scope.")
            return # If variable is already bound to the same type, do nothing
        self.table[name] = value

    def bind (self, name: str, value: Any):
        if name in self.table:
            self.table[name] = value
            return # If variable is already bound to the same type, do nothing
        if self.persistent and self.parent is not None:
            # Check if variable is already defined in a parent scope with the same type
            if self.parent.update(name, value):
                    return
        self.table[name] = value

            
    def update(self, name: str, value: Any) -> Optional[bool]:
        if name in self.table:
            self.table[name] = value
            return True # If variable is already bound to the same type, do nothing
        elif self.parent is not None and self.persistent:
            return self.parent.update(name, value)
        else:
            return False
        
    def lookup(self, name: str) -> Any:
        if name in self.table:
            return self.table[name]
        # do we use persistent here to hide for functions? 
        elif self.parent is not None:
            return self.parent.lookup(name)
        
        raise Exception(f"Variable '{name}' not found in any scope.")