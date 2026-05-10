from bosh.executor.store import Store

def test_bind_and_lookup():
    store = Store()
    loc1 = store.allocate(10)
    loc2 = store.allocate(20)
    assert store.get(loc1) == 10
    assert store.get(loc2) == 20

def test_update_value():
    store = Store()
    loc = store.allocate(5)
    assert store.get(loc) == 5
    store.set(loc, 15)
    assert store.get(loc) == 15

def test_invalid_address():
    store = Store()
    try:
        store.get(999)
        assert False, "Expected exception for invalid address"
    except Exception as e:
        assert str(e) == "Address 999 not found in store."
    
    try:
        store.set(999, 30)
        assert False, "Expected exception for invalid address"
    except Exception as e:
        assert str(e) == "Address 999 not found in store."

def test_multiple_allocations():
    store = Store()
    addresses = []
    for i in range(100):
        loc = store.allocate(i)
        addresses.append(loc)
    
    for i, loc in enumerate(addresses):
        assert store.get(loc) == i

def test_overwrite_value():
    store = Store()
    loc = store.allocate(42)
    assert store.get(loc) == 42
    store.set(loc, 84)
    assert store.get(loc) == 84

def test_nonexistent_address():
    store = Store()
    try:
        store.get(12345)
        assert False, "Expected exception for nonexistent address"
    except Exception as e:
        assert str(e) == "Address 12345 not found in store."
    
    try:
        store.set(12345, 99)
        assert False, "Expected exception for nonexistent address"
    except Exception as e:
        assert str(e) == "Address 12345 not found in store."

def test_store():
    store = Store()
    
    # Test allocation and retrieval
    loc1 = store.allocate(10)
    loc2 = store.allocate(20)
    assert store.get(loc1) == 10
    assert store.get(loc2) == 20
    
    # Test updating values
    store.set(loc1, 15)
    assert store.get(loc1) == 15
    
    # Test invalid address
    try:
        store.get(999)
        assert False, "Expected exception for invalid address"
    except Exception as e:
        assert str(e) == "Address 999 not found in store."
    
    try:
        store.set(999, 30)
        assert False, "Expected exception for invalid address"
    except Exception as e:
        assert str(e) == "Address 999 not found in store."