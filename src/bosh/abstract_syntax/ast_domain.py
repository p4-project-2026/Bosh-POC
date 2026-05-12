from .ast_base import *

@dataclass
class GoTo(ASTNode):
    path: ASTNode

    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> None:
        path_type = self.path.check(v_table, f_table)
        if path_type != "text":
            raise BoshTypeError(f"Path in 'go to' statement must be of type 'text', got '{path_type}'", self)


@dataclass
class Make(ASTNode):
    entity_type: str
    name: ASTNode
    location: ASTNode
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> None:
        if self.entity_type != "text":
            raise BoshTypeError(f"Entity type in make statement must be 'text', got '{self.entity_type}'", self)

        location_type = self.location.check(v_table, f_table) if self.location else "text"
        
        if location_type != "text":
            raise BoshTypeError(f"Path in make statement must be of type 'text', got '{location_type}'", self)

        try:
            v_table.bind(self.name.name, self.entity_type)
        except Exception as e:
            raise BoshTypeError(str(e), self)
        
        name_type = self.name.check(v_table, f_table)
        if name_type is not None and name_type != "text":
            raise BoshTypeError(f"Cannot use type '{name_type}' as a new name. Expected 'text'.", self)


@dataclass
class Delete(ASTNode):
    target: ASTNode
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> None:
        target_type = self.target.check(v_table, f_table)
        if target_type != "text":
            raise BoshTypeError(f"Cannot delete type '{target_type}'. Expected 'text'.", self)


@dataclass
class Rename(ASTNode):
    target: ASTNode
    new_name: ASTNode
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> None:
        target_type = self.target.check(v_table, f_table)
        new_name_type = self.new_name.check(v_table, f_table)
        if target_type != "text":
            raise BoshTypeError(f"Cannot rename type '{target_type}'. Expected 'text'.", self)
        if new_name_type != "text":
            raise BoshTypeError(f"New name must be of type 'text', got '{new_name_type}'", self)
        
        # try:
        #     v_table.bind(self.new_name, target_type)
        # except Exception as e:
        #     print(f"Error binding new name '{self.new_name}' to type '{target_type}'")
        #     raise BoshTypeError(str(e), self)


@dataclass
class Copy(ASTNode):
    source: ASTNode
    target: ASTNode
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> None:
        source_type = self.source.check(v_table, f_table)
        target_type = self.target.check(v_table, f_table)
        if source_type != "text":
            raise BoshTypeError(f"Cannot copy type '{source_type}'. Expected 'text'.", self)
        if target_type != "text":
            raise BoshTypeError(f"Target location in copy statement must be of type 'text', got '{target_type}'", self)
        

@dataclass
class Move(ASTNode):
    source: ASTNode
    target: ASTNode
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> None:
        source_type = self.source.check(v_table, f_table)
        target_type = self.target.check(v_table, f_table)
        if source_type != "text":
            raise BoshTypeError(f"Cannot move type '{source_type}'. Expected 'text'.", self)
        if target_type != "text":
            raise BoshTypeError(f"Target location in move statement must be of type 'text', got '{target_type}'", self)


@dataclass
class Read(ASTNode):
    source: ASTNode
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> None:
        source_type = self.source.check(v_table, f_table)
        if source_type != "text":
            raise BoshTypeError(f"Cannot read type '{source_type}'. Expected 'text'.", self)


@dataclass
class Write(ASTNode):
    target: ASTNode
    data: ASTNode
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> None:
        target_type = self.target.check(v_table, f_table)
        data_type = self.data.check(v_table, f_table)
        if target_type != "text":
            raise BoshTypeError(f"Cannot write to type '{target_type}'. Expected 'text'.", self)
        if data_type != "text":
            raise BoshTypeError(f"Data in write statement must be of type 'text', got '{data_type}'", self)


@dataclass
class GoUp(ASTNode):
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> None:
        return


@dataclass
class Execute(ASTNode):
    target: ASTNode
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> None:
        target_type = self.target.check(v_table, f_table)
        if target_type != "text":
            raise BoshTypeError(f"Cannot execute type '{target_type}'. Expected 'text'.", self)


@dataclass
class Pause(ASTNode):
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> None:
        return


@dataclass
class Wait(ASTNode):
    time: ASTNode
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> None:
        duration_type = self.time.check(v_table, f_table)
        if duration_type not in ["number", "decimal", "time"]:
            raise BoshTypeError(f"Duration in 'wait' must be of type 'number', 'decimal' or 'time', got '{duration_type}'", self)


@dataclass
class Input(ASTNode):
    prompt: Optional[ASTNode]
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        prompt_type = self.prompt.check(v_table, f_table) if self.prompt else None
        if prompt_type != "text":
            raise BoshTypeError(f"Prompt in input statement must be of type 'text', got '{prompt_type}'", self)
        return "text"