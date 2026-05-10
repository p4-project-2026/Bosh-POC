from bosh.executor.executor import Executor

from bosh.pre_processor.pre_processor import PreProcessor
from bosh.parser.parser import parseBosh, createAST
from pathlib import Path
from bosh.semantics.type_checker import TypeChecker
from bosh.app.print import *
from bosh.executor.executor import Executor


def controller(bosh_file_path):
    vprint(f"Opening File Path: \"{bosh_file_path}\"...")
    with open(bosh_file_path, "r") as f:
        content = f.read()
    vvprint(indent(content))

    vprint("Pre Processing...")
    processed_code = PreProcessor(content).run()
    vvprint(indent(processed_code))

    vprint("Parsing...")
    tree = parseBosh(processed_code)
    ast = createAST(tree, filename=bosh_file_path)
    vvprint(indent(tree.pretty()))
    vvprint(indent(ast))


    vprint("Analyzing...")
    TypeChecker().new_check(ast)
    #print("Analyzed.")

    vprint("Executing...")
    Executor().evaluate(ast)
    #print("Done.")