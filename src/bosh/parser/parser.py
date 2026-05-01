from lark import Lark, Transformer
from .ast_nodes import *
import re


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
        block = args[0]
        return Program(statements=block.statements)

    def block(self, args):
        return Block(statements=args)

    # GENERAL STATEMENTS ----------------------------------------
    def if_unable(self, args):
        return Fallback(primary_stmt=args[0], fallback_stmt=args[1])

    def if_else(self, args):
        return IfElse(
            condition=args[0],
            then_branch=args[1],
            else_branch=args[2] if len(args) > 2 else None,
        )

    def for_all(self, args):
        return ForAll(iterator_name=str(args[0]), iterable=args[1], body=args[2])

    def repeat(self, args):
        return RepeatUntil(condition=args[0], body=args[1])

    def quit(self, args):
        return Quit()

    def print(self, args):
        return Print(expression=args[0])

    def return_(self, args):
        return Return(value=args[0])

    def add_to_list(self, args):
        return ListAdd(target=args[1], element=args[0])

    def remove_from_list(self, args):
        return ListRemove(target=args[1], item=args[0])

    # DEFINITIONS ----------------------------------------
    def assign(self, args):
        return Assign(target=args[0], value=args[1])

    def assign_type(self, args):
        target = args[0]
        var_type = str(args[1])
        value = args[2] if len(args) > 2 else None
        return AssignType(target=target, var_type=var_type, value=value)

    def assign_func(self, args):
        target = args[0]
        parameters = args[1] if len(args) > 2 else []
        body = args[-1]
        return TaskDecl(name=target.name, parameters=parameters, body=body)

    # DOMAIN-SPECIFIC STATEMENTS ----------------------------------------
    def go_to(self, args):
        return GoTo(path=args[0])

    def make(self, args):
        entity_type = str(args[1])
        name = args[2].name if hasattr(args[2], "name") else str(args[2])
        return Make(entity_type=entity_type, name=name, location=args[3])

    def rename(self, args):
        return Rename(target=args[0], new_name=args[1])

    def delete(self, args):
        return Delete(target=args[0])

    def copy_from_to(self, args):
        return Copy(source=args[0], target=args[1])

    def move(self, args):
        return Move(source=args[0], target=args[1])

    def read(self, args):
        return Read(source=args[0])

    def write(self, args):
        return Write(target=args[0], data=args[1])

    # EXPRESSIONS ----------------------------------------
    def or_(self, args):
        return BinaryOp(operator="or", left=args[0], right=args[1])

    def and_(self, args):
        return BinaryOp(operator="and", left=args[0], right=args[1])

    def eq(self, args):
        right_side = str(args[1].value) if hasattr(args[1], "value") else args[1]
        return BinaryOp(operator="eq", left=args[0], right=right_side)

    def neq(self, args):
        right_side = str(args[1].value) if hasattr(args[1], "value") else args[1]
        return BinaryOp(operator="neq", left=args[0], right=right_side)

    def gt(self, args):
        return BinaryOp(operator="gt", left=args[0], right=args[1])

    def lt(self, args):
        return BinaryOp(operator="lt", left=args[0], right=args[1])

    def gte(self, args):
        return BinaryOp(operator="gte", left=args[0], right=args[1])

    def lte(self, args):
        return BinaryOp(operator="lte", left=args[0], right=args[1])

    def plus(self, args):
        return BinaryOp(operator="plus", left=args[0], right=args[1])

    def minus(self, args):
        return BinaryOp(operator="minus", left=args[0], right=args[1])

    def mult(self, args):
        return BinaryOp(operator="mult", left=args[0], right=args[1])

    def div(self, args):
        return BinaryOp(operator="div", left=args[0], right=args[1])

    def mod(self, args):
        return BinaryOp(operator="mod", left=args[0], right=args[1])

    def not_(self, args):
        return UnaryOp(operator="not", operand=args[0])

    def neg(self, args):
        return UnaryOp(operator="neg", operand=args[0])

    def length(self, args):
        return UnaryOp(operator="length", operand=args[0])

    def first(self, args):
        return UnaryOp(operator="first", operand=args[0])

    def last(self, args):
        return UnaryOp(operator="last", operand=args[0])

    def list_look(self, args):
        return ListLookup(target=args[0], index=args[1])

    def regex(self, args):
        return AccessOp(target=args[0], operation="regex", argument=args[1])

    def age(self, args):
        return AccessOp(target=args[0], operation="age")

    def file_name(self, args):
        return AccessOp(target=args[0], operation="file_name")

    def starts_with(self, args):
        return AccessOp(target=args[0], operation="starts_with", argument=args[1])

    def ends_with(self, args):
        return AccessOp(target=args[0], operation="ends_with", argument=args[1])

    def unit(self, args):
        args[1] = str(args[1])[6:-6]
        return AccessOp(target=args[0], operation="unit", argument=args[1])

    # LITERALS AND IDENTIFIERS ----------------------------------------
    def var(self, args):
        return Identifier(name=str(args[0]))

    def func(self, args):
        return TaskIdentifier(name=str(args[0]))

    def number(self, args):
        return NumberLiteral(value=int(args[0]))

    def decimal(self, args):
        return DecimalLiteral(value=float(args[0]))

    def text(self, args):
        content = str(args[0])[1:-1]
        return StringLiteral(value=content)

    def boolean(self, args):
        value_str = str(args[0]).lower()
        value = value_str == "true"
        return BooleanLiteral(value=value)

    def null(self, args):
        return NullLiteral()

    def now(self, args):
        return AccessOp(target=None, operation="now")

    def here(self, args):
        return AccessOp(target=None, operation="here")

    def paren(self, args):
        return args[0]
