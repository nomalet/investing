"""Configuration data common to Investing."""

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
root = Path(__file__).absolute().parents[3]
setpath(root)

# Path to data
data_path = setpath(root / "data/")
input_data = setpath(data_path / "input_data/")
output_data = setpath(data_path / "output_data/")
processed_data = setpath(data_path / "processed_data/")
financial_statements = setpath(input_data / "raw_statements_data/")
