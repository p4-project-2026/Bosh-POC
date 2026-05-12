from bosh.executor.scope_stack2 import ScopeStack2
from .symbol_table2 import symbol_table2
class SymbolTableScopeStacker(ScopeStack2):
    def __init__(self):
        super().__init__(table_class=symbol_table2)

    def bind(self, name: str, type_value: str):
        for scope in reversed(self.stack):
            if scope.contains(name):
                try:
                    scope.bind(name, type_value)
                except Exception as e:
                    raise Exception(f"Error binding variable '{name}': {e}")
                return
            if scope.function_scope:  # If we reach a function scope or global scope, stop searching
                break
        self.stack[-1].bind(name, type_value)  # Bind in the current scope if not found in any outer scope
    
    def bind_local(self, name: str, type_value: str):
        try:
            self.stack[-1].bind(name, type_value)
        except Exception as e:
            raise Exception(f"Error binding variable '{name}' in local scope: {e}")
        
    def domain(self) -> list[str]:
        domain = set()
        for scope in reversed(self.stack):
            domain.update(scope.domain())
        return list(domain)
    