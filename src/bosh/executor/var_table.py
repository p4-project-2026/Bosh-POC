from bosh.executor.table import Table


class VarTable(Table[int]):
    def __init__(self, function_scope: bool = False):
        super().__init__(function_scope=function_scope)
    

    
 
