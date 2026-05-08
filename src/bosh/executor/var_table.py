from bosh.executor.table import Table


class VarTable(Table[int]):
    def __init__(self, function_scope: bool = False):
        super().__init__(function_scope=function_scope)
    
    def __init__(self, table: dict[str, int]):
        self.function_scope = False
        self.table = table.copy()
    
    def get_snapshot(self):
        return self.table.copy()

    
 
