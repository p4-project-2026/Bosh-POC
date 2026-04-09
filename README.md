# Bosh POC
## Beginner Oriented Shell
### Installation
1. Install uv: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex".\venv\Scripts\activate`
2. Install dependencies: `uv sync`
### Usage
1. Run bosh script: `uv run main`
1. Run test script: `uv run test`