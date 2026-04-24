from importlib import import_module
from pathlib import Path
import pytest

def collect_test_files():
    test_directory = Path(__file__).parent / "strings"
    test_files = []
    for path in sorted(test_directory.rglob("*")):
        if path.is_file() and path.suffix == ".test":
            test_files.append(path.relative_to(test_directory))
    return test_files

@pytest.mark.parametrize("relative_path", collect_test_files())
def test_large_strings(relative_path):
    test_directory = Path(__file__).parent / "strings"
    file_path = test_directory / relative_path
    content = file_path.read_text(encoding="utf-8")

    # Split string into test_string and expected_string
    test_string, expected_string = content.split("\n===\n")
    # Extract the function name from the first line of test_string
    test_lines = test_string.splitlines()
    target_path = test_lines[0] if test_lines else ""
    test_string = "\n".join(test_lines[1:]) if len(test_lines) > 1 else ""
    
    # Dynamically import the target and call it with test_string.
    # Get class method
    if ":" in target_path:
        target_parts = target_path.split(":")
        if len(target_parts) == 2:
            class_path, function_name = target_parts
            module_path, class_name = class_path.rsplit(".", 1)
        else:
            module_path, class_name, function_name = target_parts[:3]
        target_class = getattr(import_module(module_path), class_name)
        function = getattr(target_class(test_string), function_name)
    # get function
    else:
        module_path, function_name = target_path.rsplit(".", 1)
        try:
            function = getattr(import_module(module_path), function_name)
        except ModuleNotFoundError:
            module_path, class_name = module_path.rsplit(".", 1)
            target_class = getattr(import_module(module_path), class_name)
            function = getattr(target_class(test_string), function_name)

    assert function() == expected_string, f"Test failed for {relative_path}"