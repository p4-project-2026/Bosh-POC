# Bosh POC
## Beginner Oriented Shell
### Installation
1. Install uv: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
2. Install dependencies: `uv sync`
### Usage
Run bosh script: `uv run main`
Run test script: `uv run test`
Run json parser test: `uv run .\src\bosh\json_parser\json_parser.py .\src\bosh\json_parser\test.json`