from bosh.executor.environment import Environment
from bosh.executor.function_binding import FunctionBinding

def test_environment_variable_binding_and_lookup():
    env = Environment()
    env.assign_variable("x", 42)
    assert env.lookup_variable("x") == 42

def test_environment_variable_update():
    env = Environment()
    env.assign_variable("x", 10)
    assert env.lookup_variable("x") == 10
    env.assign_variable("x", 20)
    assert env.lookup_variable("x") == 20

def test_environment_variable_not_found():
    env = Environment()
    try:
        env.lookup_variable("y")
        assert False, "Expected exception for variable not found"
    except Exception as e:
        assert str(e) == "Error looking up variable 'y': Variable 'y' not found in scope."

def test_environment_function_scope():
    env = Environment()
    env.assign_variable("a", 1)
    func_def = FunctionBinding(parameters=[], captured_scope=env.v_table.snapshot(), body=None)
    env.f_table.bind("f", func_def)
    env.enter_function_scope("f")
    assert env.lookup_variable("a") == 1
    env.assign_variable("b", 2)
    assert env.lookup_variable("b") == 2
    env.exit_scope()
    try:
        env.lookup_variable("b")
        assert False, "Expected exception for variable not found after exiting function scope"
    except Exception as e:
        assert str(e) == "Error looking up variable 'b': Variable 'b' not found in scope."
    assert env.lookup_variable("a") == 1

def test_environment_assign_variable_creates_new_variable():
    env = Environment()
    env.assign_variable("x", 5)
    assert env.lookup_variable("x") == 5

