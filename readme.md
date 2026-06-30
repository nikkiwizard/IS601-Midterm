# Calculator Project

A command-line calculator application built in Python with a REPL, operation factory, history persistence, undo/redo support, validation, logging, and CI coverage enforcement.

## Features

- REPL-based command-line interface
- Supported operations:
  - add, subtract, multiply, divide
  - modulus, int_divide, percent, abs_diff
  - power, root
- Calculation history with save/load using pandas and CSV
- Undo and redo support
- Input validation and custom exceptions
- Logging and observer-based history tracking
- Automated test coverage and CI via GitHub Actions

## Installation

### Prerequisites

- Python 3.12
- pip

### Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root if you want to override defaults.

Example:

```env
CALCULATOR_BASE_DIR=.
CALCULATOR_LOG_DIR=logs
CALCULATOR_HISTORY_FILE=history/calculator_history.csv
CALCULATOR_MAX_HISTORY_SIZE=1000
CALCULATOR_AUTO_SAVE=true
```

The app will also create the required directories automatically if they do not exist.

## Usage

Run the calculator REPL:

```bash
python main.py
```

Available commands:

- help
- add, subtract, multiply, divide
- modulus, int_divide, percent, abs_diff
- power, root
- history
- clear
- undo
- redo
- save
- load
- exit

Example:

```text
Enter command: add
Enter numbers (or 'cancel' to abort):
First number: 5
Second number: 3

Result: 8
```

## Testing

Run the full test suite:

```bash
pytest
```

## CI/CD

GitHub Actions is configured in [.github/workflows/tests.yml](.github/workflows/tests.yml) to run the test suite and enforce 90% coverage on pushes and pull requests to the main branch.

## Documentation Notes

The codebase includes docstrings and comments throughout the main modules for readability and maintainability.

- [Git Downloads](https://git-scm.com/downloads)
- [Python Downloads](https://www.python.org/downloads/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [GitHub SSH Setup Guide](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)

## Are you having issues?

I had issues getting the colorama colors to show in the terminal. While colorama is listed in the requirements file,
a quick fix is running 
```bash
python -m pip install colorama
```
locally. Please feel free to reach out with any other issues.