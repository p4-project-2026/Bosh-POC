

"""
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
"""

from typing import Optional
from bosh.executor.scope_stack2 import ScopeStack2
from bosh.executor.Store import Store
from bosh.executor.table import Table
from bosh.executor.function_binding import FunctionBinding
class Environment:
    def __init__(self):
        self.v_table = ScopeStack2()
        self.f_table = Table[FunctionBinding]()
        self.store = Store()

    def new_scope(self):
        """Create a new variable scope."""
        self.v_table.new_scope()
    def exit_scope(self):
        """Exit the current variable scope."""
        self.v_table.exit_scope()
    
    def enter_function_scope(self,name: str) -> FunctionBinding:
        """Enter a new function scope based on the function definition."""
        function_def = None
        try:
            function_def = self.f_table.lookup(name)
        except Exception as e:
            raise Exception(f"Error looking up function '{name}': {e}")
        self.v_table.enter_function_scope(function_def)
        return function_def
        
    def assign_variable(self, name: str, value: int):
        """Assign a value to a variable. If the variable already exists in any visible scope, update it. Otherwise, create a new variable in the current scope."""
        try:
            loc = self.v_table.lookup_assign(name)  # Check if variable exists in any visible scope
            self.store.set(loc, value)  # Update the value in the store
        except Exception:
            loc = self.store.allocate(value)  # Allocate a new cell in the store
            self.v_table.bind(name, loc)  # Bind the variable name to the new location in the current scope
    
    def lookup_variable(self, name: str) -> int:
        """Look up the value of a variable by name. Search through visible scopes and return the value from the store."""
        try:
            loc = self.v_table.lookup(name)  # Get the location of the variable from the scope stack
            return self.store.get(loc)  # Retrieve the value from the store using the location
        except Exception as e:
            raise Exception(f"Error looking up variable '{name}': {e}")
        
    def bind_function(self, name: str, function_def: FunctionBinding):
        """Bind a function definition to a name in the function table."""
        try:
            self.f_table.bind(name, function_def)
        except Exception as e:
            raise Exception(f"Error binding function '{name}': {e}")
        
    def __lookup_function__(self, name: str) -> FunctionBinding:
        """Look up a function definition by name."""
        try:
            return self.f_table.lookup(name)
        except Exception as e:
            raise Exception(f"Error looking up function '{name}': {e}")
