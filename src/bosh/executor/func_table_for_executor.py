from dataclasses import dataclass

from bosh.abstract_syntax.ast_base import Block
from bosh.semantics.symbol_table import SymbolTable
from bosh.executor.value_tabel import ValueTable
from typing import Dict, Optional, Any, TypeVar
@dataclass
class FunctionDef:
    parameters: list[str]
    return_type: Optional[str]
    the_function_parent_scope: ValueTable
    body: Block

    def __init__(self, parameters: Dict[str, ], return_type: Optional[str], the_function_parent_scope: ValueTable, body: Block):
        self.parameters = list(parameters.keys())
        self.return_type = return_type
        self.the_function_parent_scope = the_function_parent_scope
        self.body = body
    


def FuncTableForExecutor(SymbolTable[FunctionDef]):
    def __init__(self, parent: Optional['FuncTableForExecutor'] = None, write_through: bool = True):
        super().__init__(parent=parent, write_through=write_through)