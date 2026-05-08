from bosh.executor.var_table import VarTable

def test_var_table_bind_and_lookup():
    var_table = VarTable()
    var_table.bind("x", 42)
    assert var_table.lookup("x") == 42

def test_var_table_bind_duplicate():
    var_table = VarTable()
    var_table.bind("x", 42)
    try:
        var_table.bind("x", 43)
        assert False, "Expected exception for duplicate binding"
    except Exception as e:
        assert str(e) == "Name 'x' already defined in scope."

def test_var_table_lookup_not_found():
    var_table = VarTable()
    try:
        var_table.lookup("y")
        assert False, "Expected exception for name not found"
    except Exception as e:
        assert str(e) == "Name 'y' not found in scope."

def test_contains_and_domain():
    var_table = VarTable()
    var_table.bind("a", 1)
    var_table.bind("b", 2)
    assert var_table.contains("a") == True
    assert var_table.contains("b") == True
    assert var_table.contains("c") == False
    assert set(var_table.domain()) == {"a", "b"}

def test_function_scope():
    var_table = VarTable(function_scope=True)
    var_table.bind("f", 99)
    assert var_table.lookup("f") == 99
    assert var_table.function_scope == True

def test_get_snapshot():
    var_table = VarTable()
    var_table.bind("x", 42)
    snapshot = var_table.get_snapshot()
    assert snapshot == {"x": 42}

def test_copy():
    var_table = VarTable()
    var_table.bind("x", 42)
    copy_table = var_table.copy()
    assert copy_table.lookup("x") == 42
    copy_table.bind("y", 99)
    assert not var_table.contains("y")
    assert copy_table.contains("y")

