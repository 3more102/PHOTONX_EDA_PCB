from pathlib import Path

from ..serialization.json_policy import dumps_strict, loads_strict


def dump_json(data, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        dumps_strict(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def load_json(path: str | Path):
    return loads_strict(Path(path).read_text(encoding="utf-8"))
