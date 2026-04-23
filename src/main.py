from bosh.pre_processor.pre_processor import PreProcessor
from bosh.parser.parser import parseBosh

def main():
    with open("C:\\Users\\gunna\\Documents\\Datalogi\\Projekter\\P4\\Bosh-POC\\src\\test\\bosh_tests\\print_test.bosh", "r") as f:
        data = f.read()
    print("Test:\n" + data)
    
    processed_code = PreProcessor(data).run()
    print("Processed Code:\n" + processed_code)
    
    ast = parseBosh(processed_code)
    print("AST:\n" + str(ast))

    print("Executing...")
    # Interpreter to take the AST and execute
    print("Done.")
    
if __name__ == "__main__":
    main()
