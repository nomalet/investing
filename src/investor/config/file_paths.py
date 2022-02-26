"""Configuration data common to Toolkit."""

# Environment imports
from pathlib import Path


def setpath(filepath: Path):
    """Generates a file path if it does not exist.

    Args:
        filepath (Path): Pathlib or string of file path

    Returns:
        Pathlib: File path
    """
    # If filepath does not exist create it
    Path(filepath).mkdir(parents=True, exist_ok=True)
    return filepath


# Path to repo root
root = Path(__file__).absolute().parents[6]
setpath(root)

# Path to test data
test_data = setpath(root / "tests/test_data")
