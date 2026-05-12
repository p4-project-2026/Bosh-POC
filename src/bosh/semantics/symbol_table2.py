from bosh.executor.table import Table
class symbol_table2(Table[str]):

    def bind(self, name: str, type_value: str):
        if name in self.table:
            
            if self.table[name] == type_value:
                return # Allow re-binding to the same type
            match self.table[name]:
                case "number":
                    if type_value is "decimal":
                        self.table[name] = type_value
                        return # Allow number to be treated as decimal
                case "decimal":
                    if type_value is "number":
                        self.table[name] = type_value
                        return # Allow decimal to be treated as number
                case "any":
                    self.table[name] = type_value
                    return # Allow any to be treated as any other type
                case "list<any>":
                    if type_value.startswith("list<") or not type_value.endswith(">"):
                        self.table[name] = type_value
                        return # Allow list<any> to be treated as any other list type
                case _:
                    pass
            raise Exception(f"Variable '{name}' already bound to a different type in current scope.")
        self.table[name] = type_value
    
    def lookup(self, name: str) -> str:
        if name in self.table:
            return self.table[name]
        raise Exception(f"Variable '{name}' not found in scope.")
    
