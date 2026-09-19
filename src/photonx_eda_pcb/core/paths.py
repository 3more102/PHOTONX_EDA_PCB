from pathlib import Path, PurePosixPath, PureWindowsPath


def normalized_path(path: str | Path) -> str:
    return Path(path).as_posix()


def extension(path: str | Path) -> str:
    return Path(path).suffix.lower()


def normalize_portable_relative_path(path: str | Path) -> str:
    """Normalize a relative path without inheriting host-specific root semantics."""
    raw = str(path)
    if "\x00" in raw:
        raise ValueError("path must be a non-empty portable relative path")

    posix_path = PurePosixPath(raw.replace("\\", "/"))
    windows_path = PureWindowsPath(raw)

    if (
        not posix_path.parts
        or posix_path.is_absolute()
        or bool(windows_path.drive)
        or bool(windows_path.root)
        or ".." in posix_path.parts
    ):
        raise ValueError("path must be a non-empty portable relative path")

    return posix_path.as_posix()
