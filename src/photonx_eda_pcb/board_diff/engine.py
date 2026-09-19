from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from typing import Any

from .model import BoardDiff, DiffEntry


_MISSING = object()


class DuplicateObjectIdError(ValueError):
    """Raised when a collection contains more than one object with the same diff identity."""


class MissingObjectIdError(ValueError):
    """Raised when stable IDs are required but an object has no usable identity."""


def _default_object_id(item: Any, index: int, *, require_ids: bool) -> str:
    if isinstance(item, Mapping):
        raw_id = item.get("id", _MISSING)
    else:
        raw_id = getattr(item, "id", _MISSING)

    if raw_id is _MISSING or raw_id is None:
        if require_ids:
            raise MissingObjectIdError(
                f"object at index {index} has no stable 'id'; "
                "provide key=... or set require_ids=False"
            )
        # Backward-compatible positional fallback. Duplicate detection below
        # prevents an explicit ID such as "0" from being silently overwritten.
        return str(index)

    return str(raw_id)


def _index(
    items: Iterable[Any],
    *,
    key: Callable[[Any], object] | None,
    require_ids: bool,
) -> dict[str, Any]:
    indexed: dict[str, Any] = {}
    first_index: dict[str, int] = {}

    for index, item in enumerate(items):
        if key is None:
            object_id = _default_object_id(item, index, require_ids=require_ids)
        else:
            raw_id = key(item)
            if raw_id is None:
                raise MissingObjectIdError(
                    f"key function returned None for object at index {index}"
                )
            object_id = str(raw_id)

        if object_id in indexed:
            raise DuplicateObjectIdError(
                f"duplicate object id {object_id!r} at indexes "
                f"{first_index[object_id]} and {index}"
            )

        indexed[object_id] = item
        first_index[object_id] = index

    return indexed


def diff_collections(
    before: Iterable[Any],
    after: Iterable[Any],
    *,
    key: Callable[[Any], object] | None = None,
    require_ids: bool = False,
    equal: Callable[[Any, Any], bool] | None = None,
) -> BoardDiff:
    """Return a deterministic collection diff.

    Identity is taken from key(item) when supplied, otherwise from an id
    attribute/key. Objects without IDs retain the historical positional
    fallback unless require_ids=True.

    Duplicate identities are rejected instead of being silently overwritten.
    equal can be supplied for domain-specific comparisons such as
    tolerance-aware geometry equality.
    """

    before_index = _index(before, key=key, require_ids=require_ids)
    after_index = _index(after, key=key, require_ids=require_ids)
    is_equal = equal or (lambda left, right: left == right)

    entries: list[DiffEntry] = []

    for object_id in sorted(before_index.keys() - after_index.keys()):
        entries.append(
            DiffEntry("removed", object_id, before_index[object_id], None)
        )

    for object_id in sorted(after_index.keys() - before_index.keys()):
        entries.append(
            DiffEntry("added", object_id, None, after_index[object_id])
        )

    for object_id in sorted(before_index.keys() & after_index.keys()):
        left = before_index[object_id]
        right = after_index[object_id]
        if not is_equal(left, right):
            entries.append(DiffEntry("changed", object_id, left, right))

    return BoardDiff(entries)
