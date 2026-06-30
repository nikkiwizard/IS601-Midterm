########################
# Calculator REPL       #
########################

from decimal import Decimal
import logging
import os
import sys

try:
    from colorama import Back, Fore, Style, init
except ImportError:  # pragma: no cover - fallback for environments without colorama
    class _ColorFallback:
        BLACK = ""
        WHITE = ""
        RED = ""
        GREEN = ""
        BLUE = ""
        BRIGHT = ""
        RESET_ALL = ""

    class _ColoramaFallback:
        def init(self, *args, **kwargs):
            return None

    init = _ColoramaFallback().init
    Back = _ColorFallback()
    Fore = _ColorFallback()
    Style = _ColorFallback()

init(autoreset=False, strip=False)

from app.exceptions import OperationError, ValidationError
from app.history import AutoSaveObserver, LoggingObserver
from app.operations import OperationFactory


class _AnsiColors:
    BRIGHT = "\033[1m"
    RESET_ALL = "\033[0m"
    FG_BLACK = "\033[30m"
    FG_RED = "\033[31m"
    FG_GREEN = "\033[32m"
    FG_BLUE = "\033[34m"
    BG_WHITE = "\033[47m"
    BG_BLACK = "\033[40m"


def _supports_color() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    return sys.stdout.isatty() or os.environ.get("TERM") not in {"", "dumb"}


def format_message(message: str, message_type: str = "instruction") -> str:
    """Return a color-formatted message for the REPL."""
    if not _supports_color():
        return message

    if message_type == "instruction":
        return f"{Style.NORMAL}{Fore.BLACK}{Back.WHITE}{message}{Style.RESET_ALL}"
    if message_type == "error":
        return f"{Style.NORMAL}{Fore.BLACK}{Back.RED}{message}{Style.RESET_ALL}"
    if message_type == "result":
        return f"{Style.NORMAL}{Fore.BLACK}{Back.GREEN}{message}{Style.RESET_ALL}"
    if message_type == "input":
        return f"{Style.DIM}{Back.CYAN}{Fore.YELLOW}{message}{Style.RESET_ALL}"
    return message


def calculator_repl():  # pragma: no cover
    """
    Command-line interface for the calculator.

    Implements a Read-Eval-Print Loop (REPL) that continuously prompts the user
    for commands, processes arithmetic operations, and manages calculation history.
    """
    try:
        from app.calculator import Calculator

        # Initialize the Calculator instance
        calc = Calculator()

        # Register observers for logging and auto-saving history
        calc.add_observer(LoggingObserver())
        calc.add_observer(AutoSaveObserver(calc))

        print(format_message("Calculator started. Type 'help' for commands.", "instruction"))

        while True:
            try:
                # Prompt the user for a command
                command = input(format_message("\nEnter command: ", "input")).lower().strip()

                if command == 'help':
                    # Display available commands
                    print(format_message("Available commands:", "instruction"))
                    print(format_message("  add, subtract, multiply, divide, modulus, int_divide, percent, abs_diff, power, root - Perform calculations", "instruction"))
                    print(format_message("  history - Show calculation history", "instruction"))
                    print(format_message("  clear - Clear calculation history", "instruction"))
                    print(format_message("  undo - Undo the last calculation", "instruction"))
                    print(format_message("  redo - Redo the last undone calculation", "instruction"))
                    print(format_message("  save - Save calculation history to file", "instruction"))
                    print(format_message("  load - Load calculation history from file", "instruction"))
                    print(format_message("  exit - Exit the calculator", "instruction"))
                    continue

                if command == 'exit':
                    # Attempt to save history before exiting
                    try:
                        calc.save_history()
                        print(format_message("History saved successfully.", "result"))
                    except Exception as e:
                        print(format_message(f"Warning: Could not save history: {e}", "error"))
                    print(format_message("Goodbye!", "instruction"))
                    break

                if command == 'history':
                    # Display calculation history
                    history = calc.show_history()
                    if not history:
                        print(format_message("No calculations in history", "instruction"))
                    else:
                        print(format_message("\nCalculation History:", "instruction"))
                        for i, entry in enumerate(history, 1):
                            print(f"{i}. {entry}")
                    continue

                if command == 'clear':
                    # Clear calculation history
                    calc.clear_history()
                    print(format_message("History cleared", "instruction"))
                    continue

                if command == 'undo':
                    # Undo the last calculation
                    if calc.undo():
                        print(format_message("Operation undone", "instruction"))
                    else:
                        print(format_message("Nothing to undo", "instruction"))
                    continue

                if command == 'redo':
                    # Redo the last undone calculation
                    if calc.redo():
                        print(format_message("Operation redone", "instruction"))
                    else:
                        print(format_message("Nothing to redo", "instruction"))
                    continue

                if command == 'save':
                    # Save calculation history to file
                    try:
                        calc.save_history()
                        print(format_message("History saved successfully", "instruction"))
                    except Exception as e:
                        print(format_message(f"Error saving history: {e}", "error"))
                    continue

                if command == 'load':
                    # Load calculation history from file
                    try:
                        calc.load_history()
                        print(format_message("History loaded successfully", "instruction"))
                    except Exception as e:
                        print(format_message(f"Error loading history: {e}", "error"))
                    continue

                if command in ['add', 'subtract', 'multiply', 'divide', 'modulus', 'integer_division', 'int_divide', 'percentage', 'percent', 'absolute_difference', 'abs_diff', 'power', 'root']:
                    # Perform the specified arithmetic operation
                    try:
                        print(format_message("\nEnter numbers (or 'cancel' to abort):", "instruction"))
                        a = input(format_message("First number: ", "input"))
                        if a.lower() == 'cancel':
                            print(format_message("Operation cancelled", "instruction"))
                            continue
                        b = input(format_message("Second number: ", "input"))
                        if b.lower() == 'cancel':
                            print(format_message("Operation cancelled", "instruction"))
                            continue

                        # Create the appropriate operation instance using the Factory pattern
                        operation = OperationFactory.create_operation(command)
                        calc.set_operation(operation)

                        # Perform the calculation
                        result = calc.perform_operation(a, b)

                        # Normalize the result if it's a Decimal
                        if isinstance(result, Decimal):
                            result = result.normalize()

                        print(format_message(f"\nResult: {result}", "result"))
                    except (ValidationError, OperationError) as e:
                        # Handle known exceptions related to validation or operation errors
                        print(format_message(f"Error: {e}", "error"))
                    except Exception as e:
                        # Handle any unexpected exceptions
                        print(format_message(f"Unexpected error: {e}", "error"))
                    continue

                # Handle unknown commands
                print(format_message(f"Unknown command: '{command}'. Type 'help' for available commands.", "error"))

            except KeyboardInterrupt:
                # Handle Ctrl+C interruption gracefully
                print(format_message("\nOperation cancelled", "error"))
                continue
            except EOFError:
                # Handle end-of-file (e.g., Ctrl+D) gracefully
                print(format_message("\nInput terminated. Exiting...", "error"))
                break
            except Exception as e:
                # Handle any other unexpected exceptions
                print(f"Error: {e}")
                continue

    except Exception as e:
        # Handle fatal errors during initialization
        print(format_message(f"Fatal error: {e}", "error"))
        logging.error(f"Fatal error in calculator REPL: {e}")
        raise
