from pathlib import Path

from .walk import DEFAULT_MAX_RECURSIVE_ENTRIES, bounded_regular_files


def inventory(
    root: str | Path,
    *,
    max_entries: int = DEFAULT_MAX_RECURSIVE_ENTRIES,
) -> list[dict[str, object]]:
    root = Path(root)
    files = sorted(bounded_regular_files(root, max_entries=max_entries))
    return [
        {
            "path": p.relative_to(root).as_posix(),
            "size": p.stat().st_size,
            "suffix": p.suffix.lower(),
        }
        for p in files
    ]
