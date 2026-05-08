from bosh.executor.var_table import VarTable


class ScopeStack2:
    def __init__(self, ):
        self.stack: list[VarTable] = [VarTable()]  # Start with global scope

    def new_scope(self):
        self.stack.append(VarTable())

    def exit_scope(self):
        if len(self.stack) == 1:
            raise Exception("Cannot exit global scope.")
        self.stack.pop()


    def enter_function_scope(self, function_def):
        function_scope = function_def.the_function_parent_scope.copy(function_scope=True)
        self.stack.append(function_scope)

    def snapshot(self) -> VarTable:
        visible_scopes: list[VarTable] = []
        for scope in reversed(self.stack):
            visible_scopes.append(scope)
            if scope.function_scope:
                break  # Stop at the first function scope

        snapshot = {}

        for scope in reversed(visible_scopes):
            snapshot.update(scope.get_snapshot())
        return VarTable(table=snapshot)

    def lookup(self, name: str) -> int:
        for scope in reversed(self.stack):
            if scope.contains(name):
                return scope.lookup(name)
            if scope.function_scope:  # If we reach a function scope or global scope, stop searching
                break    
        raise Exception(f"Variable '{name}' not found in scope.")

    def bind(self, name: str, value: int):
        if self.stack[-1].contains(name):
            raise Exception(f"Variable '{name}' already defined in current scope.")
        self.stack[-1].bind(name, value)