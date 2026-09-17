from __future__ import annotations
import hashlib


def stable_id(prefix: str, *parts: object) -> str:
    """Create deterministic IDs so repeated reconstruction is diff-friendly."""
    raw = "|".join(str(p) for p in parts).encode("utf-8")
    return f"{prefix}_{hashlib.sha1(raw).hexdigest()[:12]}"
