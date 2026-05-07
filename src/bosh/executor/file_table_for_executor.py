from dataclasses import dataclass

from bosh.abstract_syntax.ast_base import Block
from bosh.semantics.symbol_table import SymbolTable
from bosh.executor.value_tabel import ValueTable
from typing import Dict, Optional, Any, TypeVar
@dataclass
class functionDef:
    parameters: Dict[str, ]
    the_function_parent_scope: ValueTable
    body: Block


def FileTableForExecutor(SymbolTable[functionDef]):