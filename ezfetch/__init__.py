"""ezfetch - A fast, cross-platform terminal system info tool."""

__version__ = "1.3.0"
__all__ = ["__version__", "main", "display"]


def main():
    """CLI entry point (lazy import to avoid RuntimeWarning with python -m)."""
    from .__main__ import main as _main
    return _main()


def display(**kwargs):
    """Public display API (lazy import)."""
    from .__main__ import display as _display
    return _display(**kwargs)
