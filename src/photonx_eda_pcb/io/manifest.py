from pathlib import Path

from .checksums import checksum_manifest
from .inventory import inventory
from .walk import DEFAULT_MAX_RECURSIVE_ENTRIES


def build_manifest(
    root: str | Path,
    *,
    max_entries: int = DEFAULT_MAX_RECURSIVE_ENTRIES,
) -> dict[str, object]:
    root = Path(root)
    return {
        "root": root.name,
        "files": inventory(root, max_entries=max_entries),
        "sha256": checksum_manifest(root, max_entries=max_entries),
    }
