from dataclasses import dataclass
from typing import Optional, Dict, Any, Type
from bosh.abstract_syntax import ast_nodes as ast
from colorama import init, Fore, Style

init(autoreset=True)

@dataclass
class Error:
    message: str #used for the error message, e.g. "Undefined variable 'x'"
    error_type: Type[Exception] = Exception #used to categorize the error, e.g. "TypeCheckError", "RuntimeError"
    severity: str = "error" #can be "error", "warning", or "info"
    details: Optional[Dict[str, Any]] = None #used to provide additional context for the error, e.g. {"expected": "int", "actual": "string"}
    suggestion: Optional[Dict[str, Any]] = None #used to provide suggestions for fixing the error, e.g. {"suggestion": "Did you mean 'y'?"}
    node_type: Optional[str] = None #used to indicate the type of AST node where the error occurred, e.g. "Assign", "Identifier", etc.
    position: Optional[ast.Position] = None #used to indicate the position in the source code where the error occurred and filename if available

class TypeCheckError(Exception):
    def __init__(self, error: Error):
        self.error = error
        super().__init__(self.format())

    def format(self) -> str:
        pos = self.error.position
        line_no = getattr(pos, 'line', None)
        filename = getattr(pos, 'filename', None)

        header = get_error_header(self.error)
        location_text = get_error_location(self.error, line_no, filename)
        context_text = get_error_context(self.error, line_no, filename)

        parts = [header, location_text, context_text]

        return "\n".join(parts).strip()

class RuntimeError(Exception):
    def __init__(self, error: Error):
        self.error = error
        super().__init__(self.format())

    def format(self) -> str:
        pass

class ErrorHandler:
    def report_error(self,
                    message: str,
                    error_type: Type[Exception],
                    node: Optional[ast.ASTNode] = None,
                    details: Optional[Dict[str, Any]] = None,
                    suggestion: Optional[Dict[str, Any]] = None):
        error = Error(
            message=message,
            error_type=error_type,
            details=details,
            suggestion=suggestion,
            node_type=type(node).__name__ if node else None,
            position=getattr(node, 'pos', None) if node else None,
        )
    
        raise error_type(error)

# Helper functions for formatting errors ---------------------------------- 

def get_error_header(error: Error) -> str:
    # Format the error header with severity, node type, message, and suggestion if available
    sev = error.severity.upper()
    node_info = f"{Style.RESET_ALL}in {Fore.CYAN}{error.node_type}{Style.RESET_ALL}" if error.node_type else ""
    suggestion_text = f". {error.suggestion}" if error.suggestion else ""
    
    return f"{Fore.RED}{sev}:{Style.RESET_ALL} {node_info}, {error.message}{suggestion_text}"

def get_error_location(error: Error, line_no: Optional[int], filename: Optional[str]) -> Optional[str]:
    # Format the error location using the position information from the error, if available
    pos = error.position
    if not pos:
        return ""

    if line_no is None or not filename:
        return ""
    
    return f"File {Fore.CYAN}{filename}{Style.RESET_ALL}, line {Fore.CYAN}{line_no}{Style.RESET_ALL}"

def get_file_line(filename: str, line_no: int) -> Optional[str]:
    # Helper function to read a specific line from a file, used for error context
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        if 1 <= line_no <= len(lines):
            return lines[line_no-1].rstrip('\n')
    except Exception:
        pass
    return None

def get_error_context(error: Error, line_no: Optional[int], filename: Optional[str]) -> str:
    pos = error.position
    source_line = get_file_line(filename, line_no)

    # Determine span for highlighting exact error location
    s_col = getattr(pos, 'start_col', None)
    e_col = getattr(pos, 'end_col', None)

    # If we have a source line and a valid span, highlight the span
    if source_line and s_col is not None and e_col is not None:
        start = max(0, s_col-1)
        end = max(start, min(len(source_line), e_col-1))
        error_line = (
            '>    ' + # indent the source line for better readability
            source_line[:start] # take everything before the error span
            + Fore.RED + source_line[start:end] + Style.RESET_ALL
            + source_line[end:] # take everything after the error span
        )
        return error_line
    return ""