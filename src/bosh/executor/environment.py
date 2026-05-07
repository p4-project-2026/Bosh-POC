from typing import Optional

from bosh.executor.value_table import ValueTable
from bosh.semantics.ScopeStack import ScopeStack
from bosh.executor.func_table_for_executor import FileTableForExecutor, FunctionDef
from bosh.abstract_syntax.ast_base import Block


class Environment:
    def __init__(self):
        self.values = [ScopeStack(ValueTable())]
        self.functions = FileTableForExecutor()
        
    def bind_value(self, name: str, value: any):
        try:
            self.values.peek().bind(name, value)
        except Exception as e:
            raise Exception(f"Error binding variable '{name}': {e}")
    def lookup_value(self, name: str) -> any:
        try:
            return self.values.peek().lookup(name)
        except Exception as e:
            raise Exception(f"Error looking up variable '{name}': {e}")
    
    def bind_function(self, name: str, parameters: list[str],  body: Block):
            function_def = FunctionDef(parameters, self.values.peek().snapshot(), body)
        
            try:
                self.functions.bind(name, function_def)
            except Exception as e:
                raise Exception(f"Error binding function '{name}': {e}")
    def lookup_function(self, name: str):
        try:
            return self.functions.lookup(name)
        except Exception as e:
            raise Exception(f"Error looking up function '{name}': {e}")
    
    def enter_function_scope(self, function_def: FunctionDef):
        function_scope = function_def.the_function_parent_scope.snapshot()
        function_scope.new_scope()
        self.values.push(function_scope)

    def fast_function_setup(self,name):
        function_def = None
        try:
            function_def = self.functions.lookup(name)
        except Exception as e:
            raise Exception(f"Error looking up function '{name}': {e}")
        self.enter_function_scope(function_def)
        return function_def

    def exit_function_scope(self):
        if self.values.len() > 1:
            self.values.pop()
        else:
            raise Exception("Cannot exit global scope.")
    def new_scope(self):
        self.values.peek().new_scope()
    
    def exit_scope(self):
        try:
            self.values.peek().exit_scope()
        except Exception as e:
            raise Exception(f"Error exiting scope: {e}")
        
    
    
    # lookup
    pass
