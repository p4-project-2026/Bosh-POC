from typing import Optional, Dict, List, TypeVar, Generic
T = TypeVar('T')

class ScopeStack(Generic[T]):
    def __init__(self):
        self.table = SymbolTable[T]()

    def new_scope(self):
        self.table = self.table.new_scope()

    def exit_scope(self):
        try:
            self.table = self.table.exit_scope()
        except Exception as e:
            raise Exception("Cannot exit global scope.")

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





class SymbolTable(Generic[T]):
    def __init__(self, parent: Optional['SymbolTable[T]'] = None):
        self.parent = parent # For nested scopes
        self.table: Dict[str, T] = {}  # Variabelnavn -> type
        
    def new_scope(self) -> 'SymbolTable[T]':
        return SymbolTable(parent=self)
    
    def exit_scope(self) -> 'SymbolTable[T]':
        if self.parent is None:
            raise Exception("Cannot exit global scope.")
        return self.parent


    # --- vtable ---

    # Bind a variable to a type in the LOCAL scope
    def bind(self, name: str, type_value: T):
        # Måske unødvendig exception, sørger for at vi ikke overskriver eksisterende variable i samme block
        if name in self.table:
            if self.table[name] != type_value:
                raise Exception(f"Variable '{name}' already bound to a different type in local scope.")
            return
        self.table[name] = type_value

 

    # Lookup a variable's type recursively through current scope, then parent scopes
    def lookup(self, name: str) -> T:
        if name in self.table:
            return self.table[name]
        
        elif self.parent is not None:
            return self.parent.lookup(name)
        
        raise Exception(f"Variable '{name}' not found in any scope.")
    
    # Check if varable is defined in the current scope
    def is_local(self, name: str) -> bool:
        return name in self.table
    
    # Return all variable names defined in the current scope, and combine with parent scopes
    def domain(self) -> List[str]:
        keys = set(self.table.keys())
        # combine with parent scopes
        if self.parent:
            keys.update(self.parent.domain())
        return list(keys)
    
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