from typing import Optional, Dict, List, TypeVar, Generic
T = TypeVar('T')


class SymbolTable(Generic[T]):
    def __init__(self, parent: Optional['SymbolTable[T]'] = None, write_through: bool = True):
        self.parent = parent # For nested scopes
        self.write_through = write_through
        self.table: Dict[str, T] = {}  # Variabelnavn -> type
        
    def new_scope(self, write_through: bool = True) -> 'SymbolTable[T]':
        return SymbolTable(parent=self, write_through=write_through)
    
    def exit_scope(self):
        if self.parent is None:
            raise Exception("Cannot exit global scope.")
        return self.parent


    def snapshot(self) -> Dict[str, T]:
        scopes = []
        scope = self
        while scope is not None:
            scopes.append(scope)
            scope = scope.parent
        
        
        snapshot_table: Dict[str, T] = {}

        for scope in reversed(scopes):
            snapshot_table.update(scope.table)
        
        
        return snapshot_table
    
    def snapshot_table(self) -> 'SymbolTable[T]':
        snapshot = SymbolTable[T]()
        snapshot.table = self.snapshot()
        return snapshot

    # --- vtable ---

    # Bind a variable to a type in the LOCAL scope
    def bind_local(self, name: str, type_value: T):
        if name in self.table:
            if self.table[name] != type_value:
                raise Exception(f"Variable '{name}' already bound to a different type in local scope.")
            return # If variable is already bound to the same type, do nothing
        self.table[name] = type_value

    def bind(self, name: str, type_value: T):
        # Måske unødvendig exception, sørger for at vi ikke overskriver eksisterende variable i samme block
        if name in self.table:
            if self.table[name] != type_value:
                raise Exception(f"Variable '{name}' already bound to a different type in current scope.")
            return # If variable is already bound to the same type, do nothing
        if self.write_through and self.parent is not None:
            # Check if variable is already defined in a parent scope with the same type
            try:
                if self.parent.update(name, type_value):
                    return
            except Exception:
                raise Exception(f"Variable '{name}' already bound to a different type in parent scope.")
        self.table[name] = type_value

 
    def update(self, name: str, type_value: T) -> bool:
        if name in self.table:
            if self.table[name] != type_value:
                raise Exception(f"Variable '{name}' already bound to a different type in accessible scope.")
            return True # If variable is already bound to the same type, do nothing
        elif self.parent is not None and self.write_through:
            return self.parent.update(name, type_value)
        else:
            return False
    
    # Lookup a variable's type recursively through current scope, then parent scopes
    def lookup(self, name: str) -> T:
        if name in self.table:
            return self.table[name]
        
        elif self.parent is not None:
            return self.parent.lookup(name)
        
        raise Exception(f"Variable '{name}' not found in any scope.")
    
    # Check if variable is defined in the current scope
    def is_local(self, name: str) -> bool:
        return name in self.table

    
    # Return all variable names defined in the current scope, and combine with parent scopes
    def domain(self) -> List[str]:
        keys = set(self.table.keys())
        # combine with parent scopes
        if self.parent:
            keys.update(self.parent.domain())
        return list(keys)
    
#    def is_in_persistent_scope_and_same_type(self, name: str, type_value: T) -> bool:
#        if name in self.table:
#            return True
#        elif self.write_through and self.parent is not None:
#            return self.parent.is_in_persistent_scope(name)
#        return False
    
    # Mayhaps implement clone from dims:
    # det er til closures.
    '''
	fun clone(): EnvAT {
        val newMap = HashMap<Var, AT>()
        for (x in bindings.entries)
            newMap.put(x.key, x.value.clone())

        return EnvAT(parentScope?.clone(), newMap)
    }
	'''

    




