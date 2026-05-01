from .flags import Flags

def vprint(*args):
    if Flags().logv:
        print(*args)

def vvprint(*args):
    if Flags().logvv:
        print(*args)

def vvvprint(*args):
    if Flags().logvvv:
        print(*args)

def indent(*args, indent_level=1):
    indent = "    " * indent_level
    result = []
    for arg in args:
        result.append(indent + str(arg).replace("\n", "\n" + indent))
    return "\n".join(result)