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

    # if no file is provided, print error and exit
    if len(args) == 0:
        print("Error: No bosh file provided.")
        exit(1)
    
    #read file path from arguments and remove it from arguments
    bosh_file_path = args[0]
    args = args[1:]
    
    if not bosh_file_path.endswith(".bosh"):
        print(f"Error: File '{bosh_file_path}' is not a .bosh file.")
        exit(1)
    
    if not Path(bosh_file_path).exists():
        print(f"Error: File '{bosh_file_path}' does not exist.")
        exit(1)

    vprint(f"executing file: {bosh_file_path} with flags: {flags} and arguments: {args}")

    controller(bosh_file_path)


if __name__ == "__main__":
    main()