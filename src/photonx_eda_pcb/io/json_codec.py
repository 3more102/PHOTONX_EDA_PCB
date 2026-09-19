import json
from pathlib import Path

from .safe_write import atomic_write_text


def dump_json(data, path: str | Path) -> Path:
    return atomic_write_text(
        path,
        json.dumps(data, indent=2, sort_keys=True) + "\n",
    )


def load_json(path: str | Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))
