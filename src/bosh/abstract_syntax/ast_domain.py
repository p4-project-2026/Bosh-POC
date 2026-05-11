from .ast_base import *

@dataclass
class GoTo(ASTNode):
    path: ASTNode

    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        path_type = self.path.check(v_table, f_table)
        if path_type not in ["text", "folder"]:
            raise BoshTypeError(f"Path in go to statement must be of type 'text' or 'folder', got '{path_type}'", self)


@dataclass
class Make(ASTNode):
    entity_type: str
    name: str
    location: ASTNode
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        if self.entity_type not in ["file", "folder"]:
            raise BoshTypeError(f"Entity type in make statement must be of type 'file' or 'folder', got '{self.entity_type}'", self)

        location_type = self.location.check(v_table, f_table)
        if location_type not in ["text", "folder"]:
            raise BoshTypeError(f"Path in make statement must be of type 'text' or 'folder', got '{location_type}'", self)

        try:
            v_table.bind(self.name, self.entity_type)
        except Exception as e:
            raise BoshTypeError(str(e), self)


@dataclass
class Delete(ASTNode):
    target: ASTNode
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        target_type = self.target.check(v_table, f_table)
        if target_type not in ["file", "folder", "text"]:
            raise BoshTypeError(f"Cannot delete type '{target_type}'. Expected file, folder, or text.", self)


@dataclass
class Rename(ASTNode):
    target: ASTNode
    new_name: str
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        target_type = self.target.check(v_table, f_table)
        if target_type not in ["file", "folder", "text"]:
            raise BoshTypeError(f"Cannot rename type '{target_type}'. Expected file, folder, or text.", self)
        
        try:
            v_table.bind(self.new_name, target_type)
        except Exception as e:
            raise BoshTypeError(str(e), self)


@dataclass
class Copy(ASTNode):
    source: ASTNode
    target: ASTNode
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        source_type = self.source.check(v_table, f_table)
        target_type = self.target.check(v_table, f_table)
        if source_type not in ["file", "folder", "text"]:
            raise BoshTypeError(f"Cannot copy type '{source_type}'. Expected file, folder, or text.", self)
        if target_type not in ["folder", "text"]:
            raise BoshTypeError(f"Target location in copy statement must be of type 'text' or 'folder', got '{target_type}'", self)
        

@dataclass
class Move(ASTNode):
    source: ASTNode
    target: ASTNode
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        source_type = self.source.accept(v_table, f_table)
        target_type = self.target.accept(v_table, f_table)
        if source_type not in ["file", "folder", "text"]:
            raise BoshTypeError(f"Cannot move type '{source_type}'. Expected file, folder, or text.", self)
        if target_type not in ["folder", "text"]:
            raise BoshTypeError(f"Target location in move statement must be of type 'text' or 'folder', got '{target_type}'", self)


@dataclass
class Read(ASTNode):
    source: ASTNode
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        source_type = self.source.check(v_table, f_table)
        if source_type not in ["file", "text"]:
            raise BoshTypeError(f"Cannot read type '{source_type}'. Expected file or text.", self)
        
        try:
            v_table.bind(self.target_name, self.target_type)
        except Exception as e:
            raise BoshTypeError(str(e), self)


@dataclass
class Write(ASTNode):
    target: ASTNode
    data: ASTNode
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        target_type = self.target.check(v_table, f_table)
        self.content.check(v_table, f_table)
        if target_type not in ["file", "text"]:
            raise BoshTypeError(f"Cannot write to type '{target_type}'. Expected file or text.", self)


@dataclass
class GoUp(ASTNode):
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        pass


@dataclass
class Execute(ASTNode):
    target: ASTNode
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        pass #MISSING


@dataclass
class Pause(ASTNode):
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        pass #MISSING

@dataclass
class Wait(ASTNode):
    time: ASTNode
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        pass #MISSING


@dataclass
class Input(ASTNode):
    prompt: Optional[ASTNode]
    
    def check(self, v_table: ScopeStack[str], f_table: FuncTable) -> Optional[str]:
        pass #MISSING