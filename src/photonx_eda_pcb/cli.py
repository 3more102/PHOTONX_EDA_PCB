from __future__ import annotations
import argparse
import json
from pathlib import Path
from .capabilities import CAPABILITIES
from .config import ReconstructionConfig
from .pipeline import reconstruct
from .reporting import summary
from .exporters import export_json, export_kicad, validate_with_kicad_cli
from .io import write_reconstruction_bundle


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="photonx", description="Evidence-driven PCB manufacturing-data reconstruction")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("capabilities")
    g = sub.add_parser("gui")
    g.add_argument("input", type=Path)
    r = sub.add_parser("reconstruct")
    r.add_argument("input", type=Path)
    r.add_argument("--output", type=Path, required=True)
    r.add_argument("--permissive", action="store_true", help="record unsupported syntax as diagnostics instead of failing")
    r.add_argument("--kicad", action="store_true", help="also emit reconstructed.kicad_pcb")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "capabilities":
        print(json.dumps([c.__dict__ for c in CAPABILITIES], indent=2))
        return 0
    if args.command == "gui":
        from .gui import launch
        launch(args.input)
        return 0
    cfg = ReconstructionConfig(strict_parsing=not args.permissive)
    result = reconstruct(args.input, cfg)
    write_reconstruction_bundle(result.board, result.validation, args.output)
    export_json(result.board, args.output / "reconstructed.json")
    if args.kicad:
        kpath = export_kicad(result.board, args.output / "reconstructed.kicad_pcb")
        ok, detail = validate_with_kicad_cli(kpath)
        (args.output / "kicad_validation.txt").write_text(f"status={ok}\n{detail}\n", encoding="utf-8")
    print(json.dumps(summary(result.board, result.validation), indent=2))
    return 0 if result.validation.ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
