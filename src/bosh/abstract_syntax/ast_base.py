from dataclasses import dataclass
from typing import List, Any, Optional
from bosh.semantics.type_checker import BoshTypeError, ScopeStack, FuncTable


@dataclass
class Position():
    line: Optional[int] = None
    start_col: Optional[int] = None
    end_col: Optional[int] = None
    filename: Optional[str] = None

# Core/base AST nodes

class ASTNode():
    pos: Optional[Position] = None

    def set_meta(self, meta, filename: Optional[str] = None):
        if meta is not None:
            self.pos = Position(
                line=meta.line,
                start_col=meta.column,
                end_col=meta.end_column,
                filename=filename
            )

    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        raise NotImplementedError(self.__class__.__name__ + " does not implement check()")
    
    def execute(self, env: 'Environment') -> Any:
        raise NotImplementedError(self.__class__.__name__ + " does not implement execute()")


@dataclass
class Program(ASTNode):
    block: Block
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        return self.block.check(v_table, f_table)
    
    def execute(self, env: 'Environment') -> Any:
        return self.block.execute(env)


@dataclass
class Block(ASTNode):
    statements: List[ASTNode]

    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        for stmt in self.statements:
            stmt.check(v_table, f_table)
        return None
    
    def execute(self, env: 'Environment') -> Any:
        for stmt in self.statements:
            stmt.execute(env)
        return None