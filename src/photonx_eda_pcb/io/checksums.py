from pathlib import Path

from ..core.hashing import sha256_file
from .walk import DEFAULT_MAX_RECURSIVE_ENTRIES, bounded_regular_files


def checksum_manifest(
    root: str | Path,
    *,
    max_entries: int = DEFAULT_MAX_RECURSIVE_ENTRIES,
) -> dict[str, str]:
    root = Path(root)
    files = sorted(bounded_regular_files(root, max_entries=max_entries))
    return {
        p.relative_to(root).as_posix(): sha256_file(p)
        for p in files
    }
