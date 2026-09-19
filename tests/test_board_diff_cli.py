from __future__ import annotations

import json

from photonx_eda_pcb.board_diff import (
    compact_diff_report,
    diff_board_paths,
    diff_board_payloads,
)
from photonx_eda_pcb.cli import main


def _payload(pads, *, metadata=None, diagnostics=None):
    return {
        "tracks": [],
        "pads": pads,
        "drills": [],
        "outline": [],
        "nets": [],
        "components": [],
        "diagnostics": diagnostics or [],
        "metadata": metadata or {},
        "slots": [],
        "routes": [],
        "regions": [],
    }


def test_board_diff_is_id_based_and_order_independent():
    before = _payload(
        [
            {"id": "P1", "size_x": 1.0},
            {"id": "P2", "size_x": 2.0},
        ]
    )
    after = _payload(
        [
            {"id": "P2", "size_x": 2.0},
            {"id": "P1", "size_x": 1.0},
        ]
    )

    report = diff_board_payloads(before, after)

    assert report["summary"] == {
        "total": 0,
        "added": 0,
        "removed": 0,
        "changed": 0,
    }
    assert report["entries"] == []


def test_board_diff_reports_per_collection_changes_deterministically():
    before = _payload(
        [
            {"id": "P1", "size_x": 1.0},
            {"id": "P2", "size_x": 2.0},
        ],
        metadata={"revision": 1},
    )
    after = _payload(
        [
            {"id": "P2", "size_x": 2.5},
            {"id": "P3", "size_x": 3.0},
        ],
        metadata={"revision": 2},
    )

    report = diff_board_payloads(before, after)

    assert report["summary"] == {
        "total": 4,
        "added": 1,
        "removed": 1,
        "changed": 2,
    }
    assert report["collections"]["pads"] == {
        "total": 3,
        "added": 1,
        "removed": 1,
        "changed": 1,
    }
    assert report["collections"]["__root__"] == {
        "total": 1,
        "added": 0,
        "removed": 0,
        "changed": 1,
    }
    assert [
        (entry["collection"], entry["kind"], entry["object_id"])
        for entry in report["entries"]
    ] == [
        ("__root__", "changed", "metadata"),
        ("pads", "removed", "P1"),
        ("pads", "added", "P3"),
        ("pads", "changed", "P2"),
    ]


def test_board_diff_accepts_reconstruction_bundle_directories(tmp_path):
    before_dir = tmp_path / "before"
    after_dir = tmp_path / "after"
    before_dir.mkdir()
    after_dir.mkdir()

    (before_dir / "board.json").write_text(
        json.dumps(_payload([{"id": "P1", "size_x": 1.0}])),
        encoding="utf-8",
    )
    (after_dir / "board.json").write_text(
        json.dumps(_payload([{"id": "P1", "size_x": 1.2}])),
        encoding="utf-8",
    )

    report = diff_board_paths(before_dir, after_dir)

    assert report["summary"]["total"] == 1
    assert report["entries"][0]["object_id"] == "P1"
    assert report["sources"]["before"].endswith("before/board.json")
    assert report["sources"]["after"].endswith("after/board.json")


def test_board_diff_cli_exit_codes_and_summary_output(tmp_path, capsys):
    before = tmp_path / "before.json"
    after = tmp_path / "after.json"
    output = tmp_path / "diff.json"

    before.write_text(
        json.dumps(_payload([{"id": "P1", "size_x": 1.0}])),
        encoding="utf-8",
    )
    after.write_text(
        json.dumps(_payload([{"id": "P1", "size_x": 2.0}])),
        encoding="utf-8",
    )

    assert main(
        [
            "diff",
            str(before),
            str(after),
            "--summary-only",
            "--output",
            str(output),
        ]
    ) == 1

    rendered = json.loads(output.read_text(encoding="utf-8"))
    assert rendered == compact_diff_report(diff_board_paths(before, after))
    assert "entries" not in rendered

    capsys.readouterr()
    assert main(["diff", str(before), str(before)]) == 0


def test_board_diff_cli_rejects_missing_input(tmp_path, capsys):
    missing = tmp_path / "missing.json"
    existing = tmp_path / "existing.json"
    existing.write_text(json.dumps(_payload([])), encoding="utf-8")

    assert main(["diff", str(missing), str(existing)]) == 2
    error = json.loads(capsys.readouterr().out)
    assert error["schema"] == "photonx.board-diff.error.v1"
    assert "does not exist" in error["error"]
