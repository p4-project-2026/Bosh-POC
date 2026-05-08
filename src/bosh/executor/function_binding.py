from bosh.executor.var_table import VarTable
from bosh.abstract_syntax.ast_base import Block


class FunctionBinding:
    def __init__(self, parameters: list[str], the_function_scope: VarTable, body: Block):
        self.parameters = parameters
        self.the_function_scope = the_function_scope
        self.body = body