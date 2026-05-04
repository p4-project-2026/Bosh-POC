from typing import Optional, Dict, List

class SymbolTable:
    def __init__(self, parent: Optional['SymbolTable'] = None):
        self.parent = parent # For nested scopes
        self.table: Dict[str, str] = {}  # Variabelnavn -> type
        
    def new_scope(self) -> 'SymbolTable':
        return SymbolTable(parent=self)

    # --- vtable ---

    # Bind a variable to a type in the LOCAL scope
    def bind(self, name: str, type_name: str):
        # Måske unødvendig exception, sørger for at vi ikke overskriver eksisterende variable i samme block
        if name in self.table:
            raise Exception(f"Variable '{name}' already bound in local scope.")
        self.table[name] = type_name

    # Update an existing variable's type, by searching recursively through current scope, then parent scopes
    def set(self, name: str, type_name: str):
        if name in self.table:
            self.table[name] = type_name
        elif self.parent is not None:
            self.parent.set(name, type_name)
        else:
            raise Exception(f"Variable '{name}' not found in any scope.")

    # Lookup a variable's type recursively through current scope, then parent scopes
    def lookup(self, name: str) -> Optional[str]:
        if name in self.table:
            return self.table[name]
        elif self.parent is not None:
            return self.parent.lookup(name)
        
        return None
    
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