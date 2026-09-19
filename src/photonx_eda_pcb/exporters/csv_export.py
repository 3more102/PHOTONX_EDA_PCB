from pathlib import Path

from ..io.safe_write import atomic_write_text
from ..reporting.csv_tables import components_csv, nets_csv


def export_csv_tables(board, directory: str | Path) -> list[Path]:
    directory = Path(directory)
    nets_path = directory / "nets.csv"
    components_path = directory / "components.csv"
    atomic_write_text(nets_path, nets_csv(board))
    atomic_write_text(components_path, components_csv(board))
    return [nets_path, components_path]
