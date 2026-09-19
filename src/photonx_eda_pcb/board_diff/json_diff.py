from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

_SCHEMA = "photonx.board-diff.v1"


def _load_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"board JSON must contain an object: {path}")
    return payload


def _resolve_board_json(path: str | Path) -> Path:
    source = Path(path)
    if source.is_dir():
        for name in ("board.json", "reconstructed.json"):
            candidate = source / name
            if candidate.is_file():
                return candidate
        raise ValueError(
            f"no board.json or reconstructed.json found in directory: {source}"
        )
    if not source.is_file():
        raise ValueError(f"board JSON does not exist: {source}")
    return source


def load_board_payload(path: str | Path) -> tuple[Path, dict[str, Any]]:
    resolved = _resolve_board_json(path)
    return resolved, _load_json_object(resolved)


def _id_map(items: Sequence[Any]) -> dict[str, Any] | None:
    indexed: dict[str, Any] = {}
    for item in items:
        if not isinstance(item, Mapping):
            return None
        object_id = item.get("id")
        if object_id is None or str(object_id) == "":
            return None
        key = str(object_id)
        if key in indexed:
            raise ValueError(f"duplicate object id in board collection: {key}")
        indexed[key] = item
    return indexed


def _entry(
    collection: str,
    kind: str,
    object_id: str,
    before: Any,
    after: Any,
) -> dict[str, Any]:
    return {
        "collection": collection,
        "kind": kind,
        "object_id": object_id,
        "before": before,
        "after": after,
    }


def _diff_sequence(
    collection: str,
    before: Sequence[Any],
    after: Sequence[Any],
) -> list[dict[str, Any]]:
    before_map = _id_map(before)
    after_map = _id_map(after)

    if before_map is None or after_map is None:
        if list(before) == list(after):
            return []
        return [_entry(collection, "changed", "__collection__", list(before), list(after))]

    entries: list[dict[str, Any]] = []
    before_ids = set(before_map)
    after_ids = set(after_map)

    for object_id in sorted(before_ids - after_ids):
        entries.append(
            _entry(collection, "removed", object_id, before_map[object_id], None)
        )
    for object_id in sorted(after_ids - before_ids):
        entries.append(
            _entry(collection, "added", object_id, None, after_map[object_id])
        )
    for object_id in sorted(before_ids & after_ids):
        if before_map[object_id] != after_map[object_id]:
            entries.append(
                _entry(
                    collection,
                    "changed",
                    object_id,
                    before_map[object_id],
                    after_map[object_id],
                )
            )
    return entries


def _summarize(entries: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counts = Counter(str(item["kind"]) for item in entries)
    return {
        "total": len(entries),
        "added": counts["added"],
        "removed": counts["removed"],
        "changed": counts["changed"],
    }


def diff_board_payloads(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    keys = sorted(set(before) | set(after))

    for key in keys:
        in_before = key in before
        in_after = key in after

        if not in_before:
            entries.append(_entry("__root__", "added", key, None, after[key]))
            continue
        if not in_after:
            entries.append(_entry("__root__", "removed", key, before[key], None))
            continue

        before_value = before[key]
        after_value = after[key]

        if (
            isinstance(before_value, list)
            and isinstance(after_value, list)
        ):
            entries.extend(_diff_sequence(key, before_value, after_value))
        elif before_value != after_value:
            entries.append(
                _entry("__root__", "changed", key, before_value, after_value)
            )

    collections: dict[str, dict[str, int]] = {}
    for collection in sorted({str(item["collection"]) for item in entries}):
        collection_entries = [
            item for item in entries if item["collection"] == collection
        ]
        collections[collection] = _summarize(collection_entries)

    return {
        "schema": _SCHEMA,
        "summary": _summarize(entries),
        "collections": collections,
        "entries": entries,
    }


def diff_board_paths(before: str | Path, after: str | Path) -> dict[str, Any]:
    before_path, before_payload = load_board_payload(before)
    after_path, after_payload = load_board_payload(after)
    report = diff_board_payloads(before_payload, after_payload)
    report["sources"] = {
        "before": str(before_path),
        "after": str(after_path),
    }
    return report


def compact_diff_report(report: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema": report.get("schema", _SCHEMA),
        "summary": dict(report.get("summary", {})),
        "collections": dict(report.get("collections", {})),
        "sources": dict(report.get("sources", {})),
    }
