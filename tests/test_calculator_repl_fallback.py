import builtins
import importlib
import sys


def test_colorama_import_fallback():
    """Reload the calculator_repl module while forcing ImportError for colorama.

    This ensures the fallback classes in the except ImportError block are executed
    and covered by tests.
    """
    real_import = builtins.__import__
    # Fake import that raises ImportError for colorama only
    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == 'colorama' or name.startswith('colorama.'):
            raise ImportError
        return real_import(name, globals, locals, fromlist, level)

    # Backup modules and inject fake import
    modules_backup = sys.modules.copy()
    builtins.__import__ = fake_import
    try:
        # Remove the module if already loaded so reload executes top-level code
        if 'app.calculator_repl' in sys.modules:
            del sys.modules['app.calculator_repl']

        # Import should now hit the ImportError fallback
        cr = importlib.import_module('app.calculator_repl')

        # Fallback should provide simple Back/Fore/Style objects
        assert hasattr(cr, 'Back')
        assert hasattr(cr, 'Fore')
        assert hasattr(cr, 'Style')

    finally:
        # Restore import and modules
        builtins.__import__ = real_import
        sys.modules.clear()
        sys.modules.update(modules_backup)
