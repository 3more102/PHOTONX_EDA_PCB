from __future__ import annotations

from pathlib import Path


DEFAULT_MAX_RECURSIVE_ENTRIES = 20_000


def bounded_regular_files(
    root: str | Path,
    *,
    max_entries: int = DEFAULT_MAX_RECURSIVE_ENTRIES,
) -> list[Path]:
    """Return regular files below *root* without unbounded tree traversal.

    Every recursively encountered entry counts against the budget, including
    directories and symlinks. File symlinks remain excluded from the returned
    set so recursive discovery cannot escape the selected input tree.
    """

    if max_entries <= 0:
        raise ValueError("max_entries must be positive")

    root = Path(root)
    files: list[Path] = []
    encountered = 0

    for path in root.rglob("*"):
        encountered += 1
        if encountered > max_entries:
            raise ValueError(
                "input tree exceeds the PHOTONX recursive discovery limit "
                f"of {max_entries} entries"
            )

        # Check the link itself before asking whether the target is a file.
        if path.is_symlink():
            continue
        if path.is_file():
            files.append(path)

    return files
