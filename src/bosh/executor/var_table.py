from bosh.executor.table import Table


class VarTable(Table[int]):
    def __init__(self, function_scope: bool = True):
        super().__init__(functionscope=function_scope)
    

    
 
