from bosh.pre_processor.pre_processor import PreProcessor
from bosh.parser.parser import parseBosh
from pathlib import Path


def main():
    with open("src/test/bosh_examples/big_example.bosh", "r") as f:
        data = f.read()
    print("Test:\n" + data)

    processed_code = PreProcessor(data).run()
    print("Processed Code:\n" + processed_code)

    ast = parseBosh(processed_code)
    print("AST:\n" + str(ast))

    print("Analyzing...")
    # Semantisk analyse
    print("Analyzed.")

    print("Executing...")
    # Interpreter
    print("Done.")


if __name__ == "__main__":
    main()