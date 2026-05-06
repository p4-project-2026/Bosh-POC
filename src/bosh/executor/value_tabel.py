from bosh.semantics.symbol_table import SymbolTable
from typing import Dict, Optional, Any, TypeVar

class ValueTable(SymbolTable[Any]):
    def __init__(self, parent: Optional['ValueTable'] = None, write_through: bool = True):
        super().__init__(parent=parent, write_through=write_through)
    
    def new_scope(self, write_through: bool = True) -> 'ValueTable':
        return ValueTable(parent=self, write_through=write_through)

    def exit_scope(self) -> 'ValueTable':
        if self.parent is None:
            raise Exception("Cannot exit global scope.")
        return self.parent
    
    def snapshot(self) -> Dict[str, Any]:
        scopes = []
        scope = self
        while scope is not None:
            scopes.append(scope)
            scope = scope.parent
        
        
        snapshot_table: Dict[str, Any] = {}

        for scope in reversed(scopes):
            snapshot_table.update(scope.table)
        
        
        return snapshot_table

    def bind_local(self, name: str, value: Any):
        #this is for x in "for all X in y"
        self.table[name] = value

    def bind (self, name: str, value: Any):
        if name in self.table:
            self.table[name] = value
            return # If variable is already bound to the same type, do nothing
        if self.write_through and self.parent is not None:
            # Check if variable is already defined in a parent scope with the same type
            if self.parent.update(name, value):
                    return
        self.table[name] = value

            
    def update(self, name: str, value: Any) -> Optional[bool]:
        if name in self.table:
            self.table[name] = value
            return True # If variable is already bound to the same type, do nothing
        elif self.parent is not None and self.write_through:
            return self.parent.update(name, value)
        else:
            return False
        
    def lookup(self, name: str) -> Any:
        if name in self.table:
            return self.table[name]
        # do we use write_through here to hide for functions? 
        elif self.parent is not None:
            return self.parent.lookup(name)
        
        raise Exception(f"Variable '{name}' not found in any scope.")