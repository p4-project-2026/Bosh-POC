from dataclasses import dataclass
from typing import List, Any, Optional
from bosh.semantics.type_checker import ScopeStack, FuncTable, FunctionSignature, BoshTypeError, BoshRuntimeError
from bosh.executor.environment import Environment

@dataclass
class Position():
    line: Optional[int] = None
    start_col: Optional[int] = None
    end_col: Optional[int] = None
    filename: Optional[str] = None


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

    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> None:
        raise BoshTypeError(self.__class__.__name__ + " does not implement check()", self)
    
    def execute(self, env: Environment) -> Any:
        raise NotImplementedError(self.__class__.__name__ + " does not implement execute()")


@dataclass
class Program(ASTNode):
    block: Block
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        return self.block.check(v_table, f_table)
    
    def execute(self, env: Environment) -> Any:
        return self.block.execute(env)


@dataclass
class Block(ASTNode):
    statements: List[ASTNode]

    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        return_type = None
        for stmt in self.statements:
            stmt_return_type = stmt.check(v_table, f_table)
            if stmt_return_type is not None:
                if return_type is not None and stmt_return_type != return_type:
                    raise BoshTypeError(f"All statements in a block must return the same type, but got '{return_type}' and '{stmt_return_type}'", self)
                return_type = stmt_return_type
        return return_type

    def execute(self, env: Environment) -> Any:
        for stmt in self.statements:
            return_val = stmt.execute(env)
            if return_val is not None:
                return return_val