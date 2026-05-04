from lark import Interpreter
from .environment import Environment
from ast_nodes import *

class Executor(Interpreter):
    # __init__
    def __init__(self):
        self.environment = Environment()

    # evaluate
    def evaluate(self):
        return self.visit(self.tree)
        
    # visit_*        