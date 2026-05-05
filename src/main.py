from pathlib import Path
import  sys

from bosh.app.controller import controller
from bosh.app.flags import Flags
from bosh.app.print import *

def main():
    # extract flags from arguments
    args = sys.argv[1:]
    flags = []
    for flag in args:
        if not flag.startswith("-"): break
        flags.append(flag)
    # remove flags from arguments
    args = args[len(flags):]

    for flag in flags: Flags().set_flag(flag)

    # if no .bosh file is provided 
    if len(args) == 0 or not args[0].endswith(".bosh"):
        bosh_file_path = "script.bosh"
        vprint(f"Warning: No .bosh file provided. Defaulting to '{bosh_file_path}'.")
    else:
        #read file path from arguments and remove it from arguments
        bosh_file_path = args[0]
        args = args[1:]
    
    if not Path(bosh_file_path).exists():
        print(f"Error: File '{bosh_file_path}' does not exist.")
        exit(1)

    vprint(f"executing file: {bosh_file_path} with flags: {flags} and arguments: {args}")

    controller(bosh_file_path)


if __name__ == "__main__":
    main()