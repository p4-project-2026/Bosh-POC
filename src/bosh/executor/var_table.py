from bosh.executor.table import Table
from typing import Dict, Optional

class VarTable(Table[int]):
    def __init__(
            self,
            function_scope: bool = False,
            table: Optional[Dict[str, int]] = None
        ):
        super().__init__(function_scope=function_scope)
        if table is not None:
            self.table = table.copy()
    
    def get_snapshot(self) -> Dict[str, int]:
        return self.table.copy()
    
    def copy(self, function_scope: Optional[bool] = None) -> 'VarTable':
        return VarTable(
            function_scope=self.function_scope if function_scope is None else function_scope,
            table=self.table
        )
    
 
