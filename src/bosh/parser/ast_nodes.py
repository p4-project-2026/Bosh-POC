from dataclasses import dataclass

# Laver dataklasser her og bruger dem i transformeren
# Gør det også nemmere at arbejde med AST'en senere i interpreter og analyzer

class ASTNode: pass

@dataclass
class Program(ASTNode):
    # Betyder at det er en liste af statements, og hver statement er en ASTNode (f.eks. PrintStatement, VarDeclaration, etc.) *mangler implementering
    statements: list[ASTNode]
