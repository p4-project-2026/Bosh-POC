from bosh.semantics.ScopeStack import ScopeStack
from bosh.semantics.symbol_table_scope_stacker import SymbolTableScopeStacker

def test_scope_stacks():
    stacker_new = SymbolTableScopeStacker()
    stacker_old = ScopeStack()
    # Test initial state
    assert stacker_new.domain() == []
    assert stacker_old.domain() == []
    # Test binding in global scope
    stacker_new.bind("x", "number")
    stacker_old.bind("x", "number")
    assert stacker_new.lookup("x") == "number"
    assert stacker_old.lookup("x") == "number"
    # Test entering new scope
    stacker_new.new_scope()
    stacker_old.new_scope()
    assert stacker_new.domain() == ["x"]
    assert stacker_old.domain() == ["x"]
    # Test binding in new scope
    stacker_new.bind("y", "string")
    stacker_old.bind("y", "string")
    assert stacker_new.lookup("y") == "string"
    assert stacker_old.lookup("y") == "string"
    # Test exiting scope
    stacker_new.exit_scope()
    stacker_old.exit_scope()
    assert stacker_new.domain() == ["x"]
    assert stacker_old.domain() == ["x"]
    # Test exiting global scope (should raise exception)
    try:
        stacker_new.exit_scope()
        assert False, "Expected exception for exiting global scope"
    except Exception as e:
        assert str(e) == "Cannot exit global scope."
    
    try:
        stacker_old.exit_scope()
        assert False, "Expected exception for exiting global scope"
    except Exception as e:
        assert str(e) == "Cannot exit global scope."

    # Test re-binding in same scope (should raise exception)
    try:
        stacker_new.bind("x", "string")
        assert False, "Expected exception for re-binding variable in same scope"
    except Exception as e:
        assert str(e) == "Error binding variable 'x': Variable 'x' already bound to a different type in current scope."
    try:
        stacker_old.bind("x", "string")
        assert False, "Expected exception for re-binding variable in same scope"
    except Exception as e:
        assert str(e) == "Variable 'x' already bound to a different type in current scope."

    # Test binding in parent scope with write-through enabled
    stacker_new.new_scope()
    stacker_old.new_scope()
    stacker_new.bind("x", "number")
    stacker_old.bind("x", "number")
    assert stacker_new.lookup("x") == "number"
    assert stacker_old.lookup("x") == "number"
    try:
            stacker_new.bind("x", "string")
            assert False, "Expected exception for re-binding variable in parent scope with write-through enabled"
    except Exception as e:
            assert str(e) == "Error binding variable 'x': Variable 'x' already bound to a different type in current scope."
    try:
            stacker_old.bind("x", "string")
            assert False, "Expected exception for re-binding variable in parent scope with write-through enabled"
    except Exception as e:
            assert str(e) == "Variable 'x' already bound to a different type in parent scope."
    stacker_new.exit_scope()
    stacker_old.exit_scope()
    assert stacker_new.lookup("x") == "number"
    assert stacker_old.lookup("x") == "number"
