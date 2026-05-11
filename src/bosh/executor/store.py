from typing import Any, Dict

class Cell:
    def __init__(
            self,
            value: Any, 
        ):
        self.value = value

class Store:
    def __init__(self):
        self.memory: Dict[int, Cell] = {}
        self.next_location: int = 0
    
    def allocate(self, value: Any) -> int:
        loc = self.next_location
        self.memory[loc] = Cell(value)
        self.next_location += 1
        return loc
    
    def get(self, address: int) -> Any:
        if address not in self.memory:
            raise Exception(f"Address {address} not found in store.")
        return self.memory[address].value

    def set(self, address: int, value: Cell):
        if address not in self.memory:
            raise Exception(f"Address {address} not found in store.")
        self.memory[address].value = value
