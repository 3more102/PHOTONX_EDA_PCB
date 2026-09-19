from __future__ import annotations

import hashlib
import json

from .canonicalize import canonical_board_dict

FINGERPRINT_SCHEMA_VERSION = 1
FINGERPRINT_SCOPE = "canonical-roundtrip-board"


def board_fingerprint(board) -> str:
    payload = canonical_board_dict(board)
    raw = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def board_fingerprint_manifest(board) -> dict[str, object]:
    return {
        "schema_version": FINGERPRINT_SCHEMA_VERSION,
        "algorithm": "sha256",
        "scope": FINGERPRINT_SCOPE,
        "sha256": board_fingerprint(board),
    }
