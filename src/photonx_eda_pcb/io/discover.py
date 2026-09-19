from pathlib import Path

GERBER_SUFFIXES = {".gbr", ".ger", ".gtl", ".gbl", ".gto", ".gbo", ".gm1"}
DRILL_SUFFIXES = {".drl", ".xln", ".exc"}


def discover_manufacturing_files(root: str | Path) -> dict[str, list[Path]]:
    root = Path(root)
    files = sorted(
        p
        for p in root.rglob("*")
        if p.is_file() and not p.is_symlink()
    )
    return {
        "gerber": [p for p in files if p.suffix.lower() in GERBER_SUFFIXES],
        "drill": [p for p in files if p.suffix.lower() in DRILL_SUFFIXES],
        "other": [
            p
            for p in files
            if p.suffix.lower() not in GERBER_SUFFIXES | DRILL_SUFFIXES
        ],
    }
