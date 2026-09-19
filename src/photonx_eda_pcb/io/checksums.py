from pathlib import Path

from ..core.hashing import sha256_file


def checksum_manifest(root: str | Path) -> dict[str, str]:
    root = Path(root)
    files = sorted(
        (
            p
            for p in root.rglob("*")
            if p.is_file() and not p.is_symlink()
        ),
        key=lambda p: (p.as_posix().lower(), p.as_posix()),
    )
    return {
        p.relative_to(root).as_posix(): sha256_file(p)
        for p in files
    }
