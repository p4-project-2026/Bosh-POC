from lark import Lark, Transformer
from .ast_nodes import *

def parseBosh(processed_code):
    with open('bosh_lang.lark', 'r') as f:
        grammar = f.read()
    
    # Laver parseren med vores grammar og specificere transformer
    # Json_parser eksemplet parser først og så transformerer i et separat trin, men gør vi det i et trin her i stedet
    parser = Lark(grammar, start='program', parser='lalr', transformer=BoshTransformer())
    return parser.parse(processed_code)

# Her laver vi vores Transformer som konverterer parse-træet til vores AST
# Hver metode i klassen svarer til en regel i vores grammar
class BoshTransformer(Transformer):
    def program(self, args):
        # Betyder at det er en liste af statements, og hver statement er en ASTNode (f.eks. PrintStatement, VarDeclaration, etc.)
        stmts = [a for a in args if isinstance(a, ASTNode)]
        return Program(stmts)