from dataclasses import dataclass

from bosh.semantics.symbol_table import SymbolTable
from typing import Optional, Any

@dataclass
class Cell:
    """
    A mutable container for a runtime value.

    ValueTable stores variables as name -> Cell instead of name -> raw value.

    This is important for closures/tasks:

        X is 1
        new task Test uses: { say X }
        X is 2

    If the task captured the Cell for X, then it can still see the updated
    value 2 later. The variable binding is snapshotted, but the Cell remains
    shared and mutable.
    """
    value: Any

class ValueTable(SymbolTable[Cell]):
    """
    Runtime value environment for Bosh.

    ValueTable maps variable names to mutable Cells:

        variable name -> Cell(value)

    This is the runtime counterpart to the type-checker's variable table.
    Where the type table stores:

        X -> "number"

    the ValueTable stores:

        X -> Cell(3)

    The table supports nested scopes through `parent`.

    `write_through` controls assignment behavior:

    - write_through=True:
        If a variable is not local, assignment may update an existing variable
        in a parent scope.

        Useful for if/repeat/while blocks where assignments to outer variables
        should persist.

    - write_through=False:
        Assignment does not pass through this scope boundary.

        Useful for function/task call scopes, where local assignment should not
        accidentally mutate captured outer variables.
    """
    def __init__(self, parent: Optional['ValueTable'] = None, write_through: bool = True):
        """
        Create a new value table scope.

        Args:
            parent:
                Parent scope. Use None for the global/root scope.

            write_through:
                Controls assignment behavior for variables found in parent
                scopes.

                True:
                    If a variable exists in a parent scope, assignment updates
                    the parent variable.

                False:
                    Assignment stays local to this scope.
        """
        super().__init__(parent=parent, write_through=write_through)
    
    def new_scope(self, write_through: bool = True) -> 'ValueTable':
        """
        Create a child scope.

        Args:
            write_through:
                Whether the new child scope should update variables in parent
                scopes when they already exist.

        Returns:
            A new ValueTable whose parent is this table.

        Example:
            global_scope = ValueTable()
            local_scope = global_scope.new_scope()
        """
        return ValueTable(parent=self, write_through=write_through)

    def exit_scope(self):
        """
        Return the parent scope.

        This does not mutate the current table by itself. The caller must assign
        the result if they want to move back to the parent scope.

        Example:
            scope = scope.new_scope()
            scope = scope.exit_scope()

        Returns:
            The parent ValueTable.

        Raises:
            Exception:
                If this table is the global/root scope.
        """
        if self.parent is None:
            raise Exception("Cannot exit global scope.")
        return self.parent
    
    def snapshot_table(self) -> 'ValueTable':
        """
        Create a snapshot copy of this value table.

        This is useful for closures, task declarations, debugging, or situations
        where the current runtime environment must be preserved.

        Returns:
            A new ValueTable containing a snapshot of the current table.

        Note:
            This depends on SymbolTable.snapshot() existing and returning a
            copied dictionary-like table.

            Depending on how snapshot() is implemented, Cells may be copied
            shallowly or deeply. If Cell values are mutable, this distinction
            matters.
        """
        snapshot = ValueTable(write_through=False)
        snapshot.table = self.snapshot()
        return snapshot

    def bind_local(self, name: str, value: Any):
        """
        Bind or update a variable in the current local scope only.

        This method never writes to parent scopes.

        It is useful for variables that should be local to a construct, such as
        loop variables.

        Example:
            for all X in Items:
                ...

            The loop variable X should usually be local to the loop body.

        Args:
            name:
                Variable name.

            value:
                Runtime value to store.
        """
        #this is for x in "for all X in y"
        if name in self.table:
            self.table[name].value = value 
            return # If variable is already bound to the same type, do nothing
        self.table[name] = Cell(value)

    def bind (self, name: str, value: Any):
        """
        Bind or update a variable.

        If the variable exists in the current scope, it is updated locally.

        If the variable does not exist locally, and write_through is True, then
        parent scopes are searched. If a parent scope contains the variable,
        that parent binding is updated.

        If the variable does not exist anywhere, it is created in the current
        scope.

        This matches assignment-like behavior:

            X is 3

        In a write-through child scope:

            X is 3
            if true: {
                X is 5
            }

        the inner assignment updates the outer X.

        Args:
            name:
                Variable name.

            value:
                Runtime value to store.
        """
        if name in self.table:
            self.table[name].value = value
            return # If variable is already bound to the same type, do nothing
        if self.write_through and self.parent is not None:
            # Check if variable is already defined in a parent scope with the same type
            if self.parent.update(name, value):
                    return
        self.table[name] = Cell(value)

            
    def update(self, name: str, value: Any) -> bool:
        """
        Update an existing variable in this scope or a parent scope.

        Unlike bind(), update() does not create a new variable if the name is
        missing. It only updates an existing binding.

        Args:
            name:
                Variable name.

            value:
                New runtime value.

        Returns:
            True if an existing variable was found and updated.
            False if the variable was not found.

        Behavior:
            - If name exists in this scope, update it and return True.
            - Else if there is a parent and write_through is True, try updating
              the parent.
            - Else return False.
        """
        if name in self.table:
            self.table[name].value = value
            return True # If variable is already bound to the same type, do nothing
        elif self.parent is not None and self.write_through:
            return self.parent.update(name, value)
        else:
            return False
        
    def lookup(self, name: str) -> Any:
        """
        Look up a variable's runtime value.

        Searches the current scope first, then recursively searches parent
        scopes.

        Args:
            name:
                Variable name.

        Returns:
            The raw runtime value stored inside the variable's Cell.

        Raises:
            Exception:
                If the variable does not exist in this scope or any parent
                scope.

        Example:
            table.bind("X", 3)
            assert table.lookup("X") == 3
        """
        if name in self.table:
            return self.table[name].value
        elif self.parent is not None:
            return self.parent.lookup(name)
        
        raise Exception(f"Variable '{name}' not found in any scope.")