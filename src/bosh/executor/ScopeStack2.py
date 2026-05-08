from inspect import stack
from typing import Dict

from bosh.executor.table import Table


class ScopeStack2:
    def __init__(self, ):
        self.stack: stack[Table[int]] = [Table[int]()]  # Start with global scope

    def new_scope(self):
        self.stack.push(Table())

    def exit_scope(self):
        if len(self.stack) == 1:
            raise Exception("Cannot exit global scope.")
        self.stack.pop()

    def lookup(self, name: str) -> int:
        for scope in reversed(self.stack):
            if scope.contains(name):
                return scope.lookup(name)
            if scope.functionscope or scope == self.stack[0]:  # If we reach a function scope or global scope, stop searching
                raise Exception(f"Variable '{name}' not found in scope.")
        
            

    def bind(self, name: str, value: int):
        if self.stack.peek().contains(name):
            raise Exception(f"Variable '{name}' already defined in current scope.")
        self.stack.peek().bind(name, value)