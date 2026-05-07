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
    def __init__(self, parent: Optional['ValueTable'] = None, child: Optional['ValueTable'] = None, write_through: bool = True):
        super().__init__(parent=parent, write_through=write_through)
        if child is not None:
            self.table = child.table

    def new_scope(self, write_through: bool = True) -> 'ValueTable':
        """
        Create a child scope whose parent is this table.

        Args:
            write_through:
                Whether assignments in the child scope may update variables
                found in parent scopes.

        Returns:
            A new ValueTable with this table as its parent.
        """
        return ValueTable(parent=self, write_through=write_through)
    

    def exit_scope(self):
        if self.parent is None:
            raise Exception("Cannot exit global scope.")
        if self.parent.parent.write_through:
            return self.parent
        raise Exception("Cannot exit function scope with exit_scope.")

    def enter_function_scope(self, value_table: 'ValueTable'):
        return ValueTable(parent=self, child=value_table, write_through=False).new_scope()

    def exit_function_scope(self):
        if self.parent is None:
            raise Exception("Cannot exit global scope.")
        if self.parent.parent is None:
            raise Exception("Cannot exit function scope from global scope.")
        if self.parent.parent.write_through:
              raise Exception("Cannot exit normal scope with exit_function_scope.")
        return self.parent.parent

    def snapshot_table(self) -> 'ValueTable':
        """
        Create a closure-style snapshot of the currently visible variables.

        The snapshot freezes which variable names are visible, but it does not
        deep-copy the values. The snapshot stores the same Cell objects.

        This means:

            X is 1
            task captures snapshot
            X is 2

        The captured snapshot still sees X, and because X's Cell is shared,
        it sees the updated value 2.

        But:

            Y is 5

        if Y is declared after the snapshot, it will not appear in the snapshot.

        Returns:
            A new ValueTable containing the visible bindings from this scope
            chain, with no parent and write_through disabled.
        """
        snapshot = ValueTable(write_through=False)
        snapshot.table = self.snapshot()
        return snapshot

    def bind_local(self, name: str, value: Any):
        """
        Bind or update a variable in the current/local scope only.

        This does not search parent scopes.

        Useful for variables that must be local, such as:

            for all Current File in here: { ... }

        where `Current File` should only exist inside the loop body.

        Args:
            name:
                Variable name.

            value:
                Runtime value to store.
        """
        if name in self.table:
            self.table[name].value = value 
            return # If variable is already bound to the same type, do nothing
        self.table[name] = Cell(value)

    def bind (self, name: str, value: Any):
        """
        Bind or assign a variable.

        Behavior:

        1. If the variable exists locally, update its Cell.
        2. Otherwise, if write_through=True, try to update an existing variable
           in a parent scope.
        3. If no existing variable is found, create a new local Cell.

        This is useful for normal assignment:

            X is 3

        Inside an if/repeat block with write_through=True, assigning to an
        existing outer X updates that outer X.

        Inside a function/task call scope with write_through=False, assigning
        to X creates or updates a local X instead of mutating the captured
        outer environment.
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
        Try to update an existing variable in this scope chain.

        This method does not create a new variable.

        Args:
            name:
                Variable name to update.

            value:
                New runtime value.

        Returns:
            True if an existing variable was found and updated.
            False if no matching variable was found before hitting a
            non-write-through boundary or the root scope.

        Notes:
            `write_through` acts as a boundary. If this table has
            write_through=False, update will not continue into its parent.
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

        Lookup always searches parent scopes, regardless of write_through.
        write_through controls writes, not reads.

        This allows function/task bodies to read captured variables without
        allowing them to mutate those variables unless the scope permits it.

        Args:
            name:
                Variable name.

        Returns:
            The runtime value stored inside the variable's Cell.

        Raises:
            Exception:
                If the variable is not found in this scope or any parent scope.
        """
        if name in self.table:
            return self.table[name].value
        elif self.parent is not None:
            return self.parent.lookup(name)
        
        raise Exception(f"Variable '{name}' not found in any scope.")