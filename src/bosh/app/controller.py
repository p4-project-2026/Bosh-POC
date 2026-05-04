from bosh.executor.executor import Executor

from bosh.pre_processor.pre_processor import PreProcessor
from bosh.parser.parser import parseBosh
from pathlib import Path

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
    # Semantisk analyse
    #print("Analyzed.")

    vprint("Executing...")
    
    #print("Done.")