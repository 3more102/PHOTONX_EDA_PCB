from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from .capabilities import CAPABILITIES
from .config import ReconstructionConfig
from .exporters import export_json, export_kicad, validate_with_kicad_cli
from .io import write_reconstruction_bundle
from .pipeline import reconstruct
from .preflight import preflight as inspect_input
from .reporting import summary


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return parsed


def _nonnegative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("value must be non-negative")
    return parsed


def _nonnegative_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed) or parsed < 0.0:
        raise argparse.ArgumentTypeError("value must be finite and non-negative")
    return parsed


def _positive_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed) or parsed <= 0.0:
        raise argparse.ArgumentTypeError("value must be positive and finite")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="photonx",
        description="Evidence-driven PCB manufacturing-data reconstruction",
    )
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("capabilities")

    nb = sub.add_parser(
        "native-benchmark",
        help="compare native and Python spatial backends on a deterministic workload",
    )
    nb.add_argument("--objects", type=_positive_int, default=1000)
    nb.add_argument("--iterations", type=_positive_int, default=3)
    nb.add_argument("--warmup", type=_nonnegative_int, default=1)
    nb.add_argument("--tolerance", type=_nonnegative_float, default=0.30)
    nb.add_argument("--radius", type=_nonnegative_float, default=1.0)
    nb.add_argument("--cell-size", type=_positive_float, default=1.0)
    nb.add_argument("--output", type=Path)

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
        help="also emit reconstructed.kicad_pcb",
    )
    return p


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "capabilities":
        print(json.dumps([c.__dict__ for c in CAPABILITIES], indent=2))
        return 0

    if args.command == "native-benchmark":
        from .benchmark_comparisons import native_spatial_benchmark_report
        from .spatial_connectivity.native_backend import (
            NativeBackendLoadError,
            NativeBackendUnavailable,
            NativeBackendUnsupported,
        )

        try:
            report = native_spatial_benchmark_report(
                args.objects,
                iterations=args.iterations,
                warmup=args.warmup,
                tolerance=args.tolerance,
                radius=args.radius,
                cell_size=args.cell_size,
            )
        except (
            NativeBackendUnavailable,
            NativeBackendLoadError,
            NativeBackendUnsupported,
            AssertionError,
        ) as exc:
            report = {
                "native_available": False,
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
            if args.output:
                _write_json(args.output, report)
            print(json.dumps(report, indent=2, sort_keys=True))
            return 2

        if args.output:
            _write_json(args.output, report)
        print(json.dumps(report, indent=2, sort_keys=True))
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

    if args.kicad:
        kpath = export_kicad(result.board, args.output / "reconstructed.kicad_pcb")
        ok, detail = validate_with_kicad_cli(kpath)
        (args.output / "kicad_validation.txt").write_text(
            f"status={ok}\n{detail}\n",
            encoding="utf-8",
        )

    print(json.dumps(summary(result.board, result.validation), indent=2))
    return 0 if result.validation.ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
