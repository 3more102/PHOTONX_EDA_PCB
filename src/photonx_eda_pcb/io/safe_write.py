import os
import tempfile
from pathlib import Path


def _best_effort_fsync_parent_directory(path: Path) -> None:
    """Persist rename metadata where directory fsync is supported.

    The data file itself is fsynced before replacement. On POSIX-like
    filesystems, fsyncing the containing directory after os.replace closes
    the remaining crash-consistency window for the directory entry. Some
    platforms/filesystems do not permit directory descriptors or directory
    fsync; those cases are intentionally best-effort so a successful replace
    is not reported as a failed write after the target has already changed.
    """
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    try:
        directory_fd = os.open(path.parent, flags)
    except OSError:
        return
    try:
        try:
            os.fsync(directory_fd)
        except OSError:
            pass
    finally:
        os.close(directory_fd)


def atomic_write_text(path: str | Path, text: str) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(
        dir=path.parent,
        prefix=path.name + ".",
        text=True,
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
        _best_effort_fsync_parent_directory(path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return path
