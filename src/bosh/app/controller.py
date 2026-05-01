from bosh.pre_processor.pre_processor import PreProcessor
from bosh.parser.parser import parseBosh
from pathlib import Path
from bosh.semantics.type_checker import TypeChecker
from bosh.app.print import *


def controller(bosh_file_path):
    vprint(f"Opening File Path: \"{bosh_file_path}\"...")
    with open(bosh_file_path, "r") as f:
        content = f.read()
    vvprint(indent(content))

    vprint("Pre Processing...")
    processed_code = PreProcessor(content).run()
    vvprint(indent(processed_code))

    vprint("Parsing...")
    ast = parseBosh(processed_code)
    vvprint(indent(ast))

    vprint("Analyzing...")
    type_checker = TypeChecker()
    type_checker.check(ast)
    #print("Analyzed.")

    vprint("Executing...")
    # Interpreter
    #print("Done.")