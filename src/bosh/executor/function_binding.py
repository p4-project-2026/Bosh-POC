from bosh.executor.var_table import VarTable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bosh.abstract_syntax.ast_base import Block


class FunctionBinding:
    def __init__(self, parameters: list[str], captured_scope: VarTable, body: "Block"):
        self.parameters = parameters
        self.captured_scope = captured_scope
        self.body = body