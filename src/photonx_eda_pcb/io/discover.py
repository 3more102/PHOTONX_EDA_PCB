from pathlib import Path

from .walk import DEFAULT_MAX_RECURSIVE_ENTRIES, bounded_regular_files


GERBER_SUFFIXES = {".gbr", ".ger", ".gtl", ".gbl", ".gto", ".gbo", ".gm1"}
DRILL_SUFFIXES = {".drl", ".xln", ".exc"}


def discover_manufacturing_files(
    root: str | Path,
    *,
    max_entries: int = DEFAULT_MAX_RECURSIVE_ENTRIES,
) -> dict[str, list[Path]]:
    root = Path(root)
    files = sorted(bounded_regular_files(root, max_entries=max_entries))
    return {
        "gerber": [p for p in files if p.suffix.lower() in GERBER_SUFFIXES],
        "drill": [p for p in files if p.suffix.lower() in DRILL_SUFFIXES],
        "other": [
            p
            for p in files
            if p.suffix.lower() not in GERBER_SUFFIXES | DRILL_SUFFIXES
        ],
    }
