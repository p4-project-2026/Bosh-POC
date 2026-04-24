from lark import Lark, Transformer
from .ast_nodes import *


def parseBosh(processed_code):
    with open("src/bosh/parser/bosh_lang.lark", "r") as f:
        grammar = f.read()

    # Laver parseren med vores grammar og specificere transformeren, som konverterer parse-træet til vores AST
    parser = Lark(grammar, start="program", parser="lalr")

    tree = parser.parse(processed_code)
    print("Parse Tree:\n" + str(tree.pretty()))

    ast = BoshTransformer().transform(tree)
    return ast


# Her laver vi vores Transformer som konverterer parse-træet til vores AST
# Hver metode i klassen svarer til en regel i vores grammar
class BoshTransformer(Transformer):
    def program(self, args):
        return Program(statements=args)

    def block(self, args):
        return Block(statements=args)

    def assign(self, args):
        return Assign(target=args[0], value=args[1])

    def assign_type(self, args):
        target = args[0]
        var_type = args[1]
        value = args[2] if len(args) > 2 else None
        return AssignType(target=target, var_type=var_type, value=value)

    def print(self, args):
        return Print(expression=args[0])

    def var(self, args):
        return Identifier(name=str(args[0]))

    def text(self, args):
        content = str(args[0])[1:-1]
        return StringLiteral(value=content)