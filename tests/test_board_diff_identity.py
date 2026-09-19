from dataclasses import dataclass

import pytest

from photonx_eda_pcb.board_diff.engine import (
    DuplicateObjectIdError,
    MissingObjectIdError,
    diff_collections,
)
from photonx_eda_pcb.board_diff.model import BoardDiff, DiffEntry
from photonx_eda_pcb.board_diff.validation import validate_diff


@dataclass(frozen=True)
class Obj:
    id: str
    value: float


@dataclass(frozen=True)
class NoId:
    value: int


def test_mapping_id_is_used_as_stable_identity():
    diff = diff_collections(
        [{"id": "a", "value": 1}, {"id": "b", "value": 2}],
        [{"id": "b", "value": 3}, {"id": "c", "value": 4}],
    )

    assert [(entry.kind, entry.object_id) for entry in diff.entries] == [
        ("removed", "a"),
        ("added", "c"),
        ("changed", "b"),
    ]


def test_duplicate_object_ids_fail_instead_of_overwriting():
    with pytest.raises(DuplicateObjectIdError, match="duplicate object id 'a'"):
        diff_collections([Obj("a", 1), Obj("a", 2)], [])


def test_positional_fallback_cannot_silently_collide_with_explicit_id():
    with pytest.raises(DuplicateObjectIdError, match="duplicate object id '0'"):
        diff_collections([NoId(1), Obj("0", 2)], [])


def test_require_ids_rejects_positional_fallback():
    with pytest.raises(MissingObjectIdError, match="no stable 'id'"):
        diff_collections([NoId(1)], [NoId(1)], require_ids=True)


def test_custom_key_supports_domain_specific_stable_identity():
    before = [{"stable": "x", "value": 1}]
    after = [{"stable": "x", "value": 2}]

    diff = diff_collections(before, after, key=lambda item: item["stable"])

    assert [(entry.kind, entry.object_id) for entry in diff.entries] == [
        ("changed", "x"),
    ]


def test_custom_equality_can_apply_numeric_tolerance():
    before = [Obj("a", 1.0)]
    after = [Obj("a", 1.0005)]

    diff = diff_collections(
        before,
        after,
        equal=lambda left, right: left.id == right.id
        and abs(left.value - right.value) <= 0.001,
    )

    assert diff.entries == []


def test_validate_diff_rejects_repeated_identity_and_invalid_payloads():
    diff = BoardDiff(
        [
            DiffEntry("added", "a", None, Obj("a", 1)),
            DiffEntry("changed", "a", None, Obj("a", 2)),
        ]
    )

    assert validate_diff(diff) == [
        "DIFF_OBJECT_ID_REPEATED",
        "DIFF_PAYLOAD_INVALID",
    ]
