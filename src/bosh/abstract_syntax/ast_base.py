from dataclasses import dataclass
from typing import List, Any, Optional

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

    def accept(self, visitor) -> Any:
        raise NotImplementedError()


@dataclass
class Program(ASTNode):
    block: Block
    def accept(self, visitor) -> Any:
        return visitor.visit_Program(self)


@dataclass
class Block(ASTNode):
    statements: List[ASTNode]
    def accept(self, visitor) -> Any:
        return visitor.visit_Block(self)