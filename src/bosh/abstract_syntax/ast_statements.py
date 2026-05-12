from .ast_base import *

@dataclass
class Print(ASTNode):
    expression: ASTNode

    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        self.expression.check(v_table, f_table)


@dataclass
class IfElse(ASTNode):
    condition: ASTNode
    then_branch: Block
    else_branch: Optional[Block]
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        condition_type = self.condition.check(v_table, f_table)
        if condition_type != "boolean":
            raise BoshTypeError(f"Condition in if statement must be of type 'boolean', got '{condition_type}'", self)
        
        try:
            v_table.new_scope()
            self.then_branch.check(v_table, f_table)
            v_table.exit_scope()
        except Exception as e:
            raise BoshTypeError(str(e), self)
        
        if self.else_branch:            
            try:
                v_table.new_scope()
                self.else_branch.check(v_table, f_table)
                v_table.exit_scope()
            except Exception as e:
                raise BoshTypeError(str(e), self)


@dataclass
class Fallback(ASTNode):
    primary_stmt: ASTNode
    fallback_stmt: ASTNode
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        self.primary_stmt.check(v_table, f_table)
        self.fallback_stmt.check(v_table, f_table)


@dataclass
class ForAll(ASTNode):
    iterator_name: str
    iterable: ASTNode
    body: Block
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        iterable_type = self.iterable.check(v_table, f_table)
        if iterable_type is None:
            return
        if iterable_type not in ["file", "folder", "text"] and not (iterable_type.startswith("list<") and iterable_type.endswith(">")):
            raise BoshTypeError(f"Iterable in for all statement must be of type 'list', 'file', 'folder', or 'text', got '{iterable_type}'", self)
        
        element_type = iterable_type[5:-1] 
        v_table.new_scope()
        try:
            v_table.bind(self.iterator_name, element_type)
            self.body.check(v_table, f_table)
        except Exception as e:
            raise BoshTypeError(str(e), self)
        finally:
            try:
                v_table.exit_scope()
            except Exception as e:
                raise BoshTypeError(str(e), self)
        

@dataclass
class RepeatUntil(ASTNode):
    condition: ASTNode
    body: Block
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        condition_type = self.condition.check(v_table, f_table)
        if condition_type != "boolean":
            raise BoshTypeError(f"Condition in repeat until statement must be of type 'boolean', got '{condition_type}'", self)
        self.body.check(v_table, f_table)

@dataclass
class Quit(ASTNode):
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        return


@dataclass
class ListAdd(ASTNode):
    target: ASTNode
    item: ASTNode
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        target_type = self.target.check(v_table, f_table)
        self.item.check(v_table, f_table)

        if not target_type.startswith("list<") or not target_type.endswith(">"):
            raise BoshTypeError(f"Cannot add to type '{target_type}'. Can only add to lists.", self)
        
        if target_type == "list<any>":
            item_type = self.item.check(v_table, f_table)
            try:
                v_table.bind(self.target.name, f"list<{item_type}>")
            except Exception as e:
                raise BoshTypeError(str(e), self)


@dataclass
class ListRemove(ASTNode):
    target: ASTNode
    item: ASTNode
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        target_type = self.target.check(v_table, f_table)
        self.item.check(v_table, f_table)
        if not target_type.startswith("list<") or not target_type.endswith(">"):
            raise BoshTypeError(f"Cannot remove from type '{target_type}'. Can only remove from lists.", self)


@dataclass
class Return(ASTNode):
    expression: ASTNode
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        return self.expression.check(v_table, f_table)