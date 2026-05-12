from typing import Optional
from bosh.executor.scope_stack2 import ScopeStack2
from bosh.executor.store import Store
from bosh.executor.table import Table
from bosh.executor.function_binding import FunctionBinding
from bosh.executor.var_table import VarTable
from pathlib import Path
class Environment:
    def __init__(self):
        self.v_table = ScopeStack2[int](VarTable)
        self.f_table = Table[FunctionBinding]()
        self.store = Store()
        self.CD: str = str(Path.cwd())  # Current Directory, used for resolving file paths in import statements

    def new_scope(self):
        """Create a new variable scope."""
        self.v_table.new_scope()
    def exit_scope(self):
        """Exit the current variable scope."""
        self.v_table.exit_scope()
    
    def enter_function_scope(self,name: str) -> FunctionBinding:
        """Enter a new function scope based on the function definition associated with the given name. returns the FunctionBinding for the function being entered."""
        function_def = None
        try:
            function_def = self.f_table.lookup(name)
        except Exception as e:
            raise Exception(f"Error looking up function '{name}': {e}")
        self.v_table.enter_function_scope(function_def)
        return function_def
        
    def assign_variable(self, name: str, value: int):
        """Assign a value to a variable. If the variable already exists in any assingnable scope, update its value. Otherwise, create a new variable in the current scope."""
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
    
    def snapshot(self) -> VarTable:
        """Create a snapshot of the current variable scope stack. This is used for capturing the environment when defining a function."""
        return self.v_table.snapshot()
    
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

    def get_current_directory(self) -> str:
        """Get the current directory for resolving file paths in import statements."""
        return self.CD
    
    def set_current_directory(self, path: str):
        """Set the current directory for resolving file paths in import statements."""
        self.CD = path