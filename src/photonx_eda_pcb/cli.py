from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .capabilities import CAPABILITIES
from .config import ReconstructionConfig
from .exporters import (
    export_csv_tables,
    export_graphml,
    export_json,
    export_kicad_with_report,
    export_svg,
    validate_with_kicad_cli,
    write_omission_manifest,
)
from .io import write_reconstruction_bundle
from .pipeline import reconstruct
from .preflight import preflight as inspect_input
from .reporting import summary
from .reporting.json_report import render_json_report
from .reporting.junit import checks_to_junit
from .reporting.markdown import render_markdown_report
from .roundtrip import validate_kicad_connectivity_roundtrip


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="photonx",
        description="Evidence-driven PCB manufacturing-data reconstruction",
    )
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("capabilities")

    pf = sub.add_parser(
        "preflight",
        help="inspect a folder/file/archive and report parser compatibility",
    )
    pf.add_argument("input", type=Path)
    pf.add_argument("--output", type=Path)

    g = sub.add_parser("gui")
    g.add_argument("input", type=Path)

    r = sub.add_parser("reconstruct")
    r.add_argument(
        "input",
        type=Path,
        help="Gerber/Excellon directory, single file, ZIP, TAR, or TGZ package",
    )
    r.add_argument("--output", type=Path, required=True)
    r.add_argument(
        "--permissive",
        action="store_true",
        help="record unsupported syntax as diagnostics instead of failing",
    )
    r.add_argument(
        "--kicad",
        action="store_true",
        help="also emit reconstructed.kicad_pcb plus KiCad audit, round-trip, and validation artifacts",
    )
    r.add_argument(
        "--review-artifacts",
        action="store_true",
        help=(
            "emit a review bundle under OUTPUT/review "
            "(Markdown, JSON, JUnit, SVG, GraphML, and CSV)"
        ),
    )
    r.add_argument(
        "--svg",
        action="store_true",
        help="also emit reconstructed.svg for lightweight visual review",
    )
    r.add_argument(
        "--graphml",
        action="store_true",
        help="also emit reconstructed.graphml for connectivity analysis",
    )
    r.add_argument(
        "--csv",
        action="store_true",
        help="also emit csv/nets.csv and csv/components.csv summaries",
    )
    return p


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _write_text(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _write_kicad_export_report(path: Path, report) -> Path:
    payload = asdict(report)
    payload["ok"] = bool(report.ok)
    _write_json(path, payload)
    return path


def _write_review_artifacts(board, output_dir: Path) -> list[Path]:
    review_dir = Path(output_dir) / "review"
    artifacts = [
        _write_text(review_dir / "report.md", render_markdown_report(board)),
        _write_text(review_dir / "summary.json", render_json_report(board)),
        _write_text(review_dir / "checks.junit.xml", checks_to_junit(board) + "\n"),
        export_svg(board, review_dir / "board.svg"),
        export_graphml(board, review_dir / "connectivity.graphml"),
    ]
    artifacts.extend(export_csv_tables(board, review_dir / "csv"))
    return artifacts


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "capabilities":
        print(json.dumps([c.__dict__ for c in CAPABILITIES], indent=2))
        return 0

    if args.command == "preflight":
        report = inspect_input(args.input).to_dict()
        if args.output:
            _write_json(args.output, report)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report["discovered_files"] else 2

    if args.command == "gui":
        from .gui import launch

        launch(args.input)
        return 0

    report = inspect_input(args.input).to_dict()
    args.output.mkdir(parents=True, exist_ok=True)
    _write_json(args.output / "input_preflight.json", report)

    if not report["discovered_files"]:
        print(json.dumps(report, indent=2, sort_keys=True))
        return 2

    if not args.permissive and not report["ready_for_strict_reconstruction"]:
        print(json.dumps(report, indent=2, sort_keys=True))
        return 3

    cfg = ReconstructionConfig(strict_parsing=not args.permissive)
    result = reconstruct(args.input, cfg)
    write_reconstruction_bundle(result.board, result.validation, args.output)
    export_json(result.board, args.output / "reconstructed.json")

    if args.review_artifacts:
        _write_review_artifacts(result.board, args.output)

    if args.svg:
        export_svg(result.board, args.output / "reconstructed.svg")

    if args.graphml:
        export_graphml(result.board, args.output / "reconstructed.graphml")

    if args.csv:
        export_csv_tables(result.board, args.output / "csv")

    if args.kicad:
        kpath, export_report = export_kicad_with_report(
            result.board,
            args.output / "reconstructed.kicad_pcb",
        )
        _write_kicad_export_report(
            args.output / "kicad_export_report.json",
            export_report,
        )
        write_omission_manifest(
            export_report,
            args.output / "kicad_omissions.json",
        )
        _write_json(
            args.output / "kicad_connectivity_roundtrip.json",
            validate_kicad_connectivity_roundtrip(
                result.board,
                kpath,
                export_report,
            ),
        )
        ok, detail = validate_with_kicad_cli(kpath)
        (args.output / "kicad_validation.txt").write_text(
            f"status={ok}\n{detail}\n",
            encoding="utf-8",
        )

    print(json.dumps(summary(result.board, result.validation), indent=2))
    return 0 if result.validation.ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
