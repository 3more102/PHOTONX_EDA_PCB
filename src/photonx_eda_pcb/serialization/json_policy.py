from __future__ import annotations

import json
from typing import Any


def _reject_non_finite_constant(token: str) -> None:
    raise ValueError(f"non-finite JSON numeric literal is not permitted: {token}")


def _reject_duplicate_object_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key is not permitted: {key!r}")
        result[key] = value
    return result


def dumps_strict(value: Any, **kwargs: Any) -> str:
    """Serialize standards-compliant JSON and reject NaN/Infinity values."""
    kwargs["allow_nan"] = False
    return json.dumps(value, **kwargs)


def loads_strict(text: str | bytes | bytearray, **kwargs: Any) -> Any:
    """Parse JSON while rejecting non-finite numbers and duplicate object keys."""
    if "parse_constant" in kwargs or "object_pairs_hook" in kwargs:
        raise TypeError(
            "loads_strict controls parse_constant and object_pairs_hook to enforce strict JSON"
        )
    return json.loads(
        text,
        parse_constant=_reject_non_finite_constant,
        object_pairs_hook=_reject_duplicate_object_keys,
        **kwargs,
    )
