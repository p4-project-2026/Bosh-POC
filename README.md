# Bosh POC
## Beginner Oriented Shell
## Installation
1. Install uv: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
2. Install dependencies: `uv sync`
## Usage
Run bosh: `uv run main [-flags] [file] [args]
Run test: `pytest`

### File
default file `script.bosh`

### Flags
- `v`: Verbose output
- `vv`: Very verbose output
- `vvv`: Very very verbose output

### Log file
Append `[> | >>] [file]`
- `>`: overwrite
- `>>`: append