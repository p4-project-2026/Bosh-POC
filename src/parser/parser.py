import sys
from lark import Lark
parser = Lark.open('test.lark', rel_to=__file__, parser='lalr')