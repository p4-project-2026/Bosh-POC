from .ast_base import *

@dataclass
class Print(ASTNode):
    expression: ASTNode

    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> None:
        self.expression.check(v_table, f_table)


@dataclass
class IfElse(ASTNode):
    condition: ASTNode
    then_branch: Block
    else_branch: Optional[Block]
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> None:
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
            
    def execute(self, env: Environment) -> None:
        condition_value = self.condition.execute(env)
        if condition_value:
            env.new_scope()
            try:
                self.then_branch.execute(env)
            finally:
                env.exit_scope()
        elif self.else_branch:
            env.new_scope()
            try:
                self.else_branch.execute(env)
            finally:
                env.exit_scope()


@dataclass
class Fallback(ASTNode):
    primary_stmt: ASTNode
    fallback_stmt: ASTNode
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> None:
        self.primary_stmt.check(v_table, f_table)
        self.fallback_stmt.check(v_table, f_table)

    def execute(self, env: Environment) -> None:
        try:
            self.primary_stmt.execute(env)
        except Exception:
            self.fallback_stmt.execute(env)

@dataclass
class ForAll(ASTNode):
    iterator_name: str
    iterable: ASTNode
    body: Block
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> None:
        iterable_type = self.iterable.check(v_table, f_table)
        if iterable_type is None:
            return
        if iterable_type != "text" and not (iterable_type.startswith("list<") and iterable_type.endswith(">")):
            raise BoshTypeError(f"Iterable in for all statement must be of type 'list' or 'text', got '{iterable_type}'", self)
        element_type = iterable_type[5:-1] if iterable_type.startswith("list<") else "text"
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
        
    def execute(self, env: Environment) -> None:
        iterable_value = self.iterable.execute(env)
        if iterable_value is None:
            return
        if isinstance(iterable_value, str):
            iterable_value = [iterable_value]
        
        for item in iterable_value:
            env.new_scope()
            try:
                env.assign_variable(self.iterator_name, item)
                self.body.execute(env)
            finally:
                env.exit_scope()

@dataclass
class RepeatUntil(ASTNode):
    condition: ASTNode
    body: Block
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> None:
        condition_type = self.condition.check(v_table, f_table)
        if condition_type != "boolean":
            raise BoshTypeError(f"Condition in repeat until statement must be of type 'boolean', got '{condition_type}'", self)
        self.body.check(v_table, f_table)

    def execute(self, env: Environment) -> None:
        env.new_scope()

        while True:
            self.body.execute(env)
            condition_value = self.condition.execute(env)
            if condition_value:
                break
        
        env.exit_scope()

@dataclass
class Quit(ASTNode):
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> None:
        return
    
    def execute(self, env: Environment) -> None:
        raise SystemExit()


@dataclass
class ListAdd(ASTNode):
    target: ASTNode
    item: ASTNode
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> None:
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

    def execute(self, env: Environment) -> None:
        target_value = self.target.execute(env)
        item_value = self.item.execute(env)
        target_value.append(item_value)


@dataclass
class ListRemove(ASTNode):
    target: ASTNode
    item: ASTNode
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        target_type = self.target.check(v_table, f_table)
        self.item.check(v_table, f_table)
        if not target_type.startswith("list<") or not target_type.endswith(">"):
            raise BoshTypeError(f"Cannot remove from type '{target_type}'. Can only remove from lists.", self)

    def execute(self, env: Environment) -> None:
        target_value = self.target.execute(env)
        item_value = self.item.execute(env)
        try:
            target_value.remove(item_value)
        except ValueError:
            raise Exception(f"Item '{item_value}' not found in list.")
        
@dataclass
class ListRemoveAt(ASTNode):
    target: ASTNode
    index: ASTNode
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        target_type = self.target.check(v_table, f_table)
        index_type = self.index.check(v_table, f_table)
        if not target_type.startswith("list<") or not target_type.endswith(">"):
            raise BoshTypeError(f"Cannot remove from type '{target_type}'. Can only remove from lists.", self)
        if index_type != "int":
            raise BoshTypeError(f"Index in list remove at statement must be of type 'int', got '{index_type}'", self)

    def execute(self, env: Environment) -> None:
        target_value = self.target.execute(env)
        index_value = self.index.execute(env)
        try:
            del target_value[index_value]
        except IndexError:
            raise Exception(f"Index '{index_value}' out of range for list.")

@dataclass
class Return(ASTNode):
    expression: ASTNode
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        return self.expression.check(v_table, f_table)
    
    def execute(self, env: Environment) -> Any:
        return self.expression.execute(env)