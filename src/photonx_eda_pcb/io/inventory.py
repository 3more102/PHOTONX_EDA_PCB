from pathlib import Path


def inventory(root: str | Path) -> list[dict[str, object]]:
    root = Path(root)
    files = sorted(
        p
        for p in root.rglob("*")
        if p.is_file() and not p.is_symlink()
    )
    return [
        {
            "path": p.relative_to(root).as_posix(),
            "size": p.stat().st_size,
            "suffix": p.suffix.lower(),
        }
        for p in files
    ]
