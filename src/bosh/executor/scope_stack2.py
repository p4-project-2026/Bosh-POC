from bosh.executor.table import Table
from bosh.executor.function_binding import FunctionBinding
from typing import TypeVar, Generic, Type, Dict

T = TypeVar('T')


class ScopeStack2(Generic[T]):
    def __init__(self, table_class: Type[Table[T]] = Table):
        self.table_class = table_class
        self.stack: list[Table[T]] = [self.table_class()]  # Start with global scope

    def new_scope(self):
        self.stack.append(self.table_class())

    def exit_scope(self):
        if len(self.stack) == 1:
            raise Exception("Cannot exit global scope.")
        if self.stack[-2].function_scope:
            self.stack.pop()  # pop function body scope
            self.stack.pop()  # pop captured function boundary scope
            return
        self.stack.pop()


    def enter_function_scope(self, function_def: FunctionBinding):
        function_scope = function_def.captured_scope.copy(function_scope=True)
        self.stack.append(function_scope)
        self.new_scope()  # Create a new scope for the function body

    def snapshot(self) -> Table[T]:
        visible_scopes: list[Table[T]] = []
        for scope in reversed(self.stack):
            visible_scopes.append(scope)
            if scope.function_scope:
                break  # Stop at the first function scope

        snapshot: Dict[str, T] = {}

        for scope in reversed(visible_scopes):
            snapshot.update(scope.get_snapshot())

        return self.table_class(table=snapshot)

    def lookup(self, name: str) -> T:
        for scope in reversed(self.stack):
            if scope.contains(name):
                return scope.lookup(name)
            if scope.function_scope:  # If we reach a function scope or global scope, stop searching
                break    
        raise Exception(f"Variable '{name}' not found in scope.")
    
    def lookup_assign(self, name: str) -> T:
        for scope in reversed(self.stack):
            if scope.function_scope:  # If we reach a function scope or global scope, stop searching
                break    
            if scope.contains(name):
                return scope.lookup(name)
        raise Exception(f"Variable '{name}' not found in scope.")

    def bind(self, name: str, value: T):
        if self.stack[-1].contains(name):
            raise Exception(f"Variable '{name}' already defined in current scope.")
        self.stack[-1].bind(name, value)

    def domain(self) -> list[str]:
        domain = {}
        for scope in reversed(self.stack):
            domain.update({name: None for name in scope.domain()})