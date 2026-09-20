from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import ReconstructionConfig
from .connectivity import attach_drills, build_physical_graph, assign_physical_nets
from .inference import infer_component_hypotheses
from .input_package import prepare_input
from .models import BoardModel, ParseDiagnostic
from .parsers import discover_manufacturing_files, GerberRS274XParser, ExcellonParser
from .stackup import infer_stackup
from .validation import ValidationReport, validate_board
from .via_span import resolve_via_spans


@dataclass
class ReconstructionResult:
    board: BoardModel
    validation: ValidationReport


def _serialize_via_spans(spans):
    return [
        {
            "drill_id": span.drill_id,
            "from_layer": span.from_layer,
            "to_layer": span.to_layer,
            "confidence": span.confidence,
            "proven": span.proven,
            "pad_ids": list(span.pad_ids),
            "evidence": list(span.evidence),
        }
        for span in spans
    ]


def _apply_file_plating_hint(board: BoardModel, item, drills) -> None:
    hint = getattr(item, "plating_hint", None)
    if hint not in {"plated", "non-plated"}:
        return

    changed_ids = []
    for drill in drills:
        if drill.plating != "unknown":
            continue
        drill.plating = hint
        changed_ids.append(drill.id)

    if not changed_ids:
        return

    evidence = board.metadata.setdefault("drill_plating_evidence", [])
    evidence.append(
        {
            "path": str(item.path),
            "plating": hint,
            "source": "explicit_filename_token",
            "drill_ids": changed_ids,
        }
    )


def _report_unproven_multilayer_spans(board: BoardModel, spans) -> None:
    drill_by_id = {drill.id: drill for drill in board.drills}
    source_path = str(board.metadata.get("source_input", ""))
    for span in spans:
        if (
            span.proven
            or span.from_layer is None
            or span.to_layer is None
            or span.from_layer == span.to_layer
        ):
            continue
        drill = drill_by_id.get(span.drill_id)
        if drill is None or drill.plating != "unknown":
            continue
        board.diagnostics.append(
            ParseDiagnostic(
                "warning",
                "MULTILAYER_SPAN_UNKNOWN",
                (
                    f"{span.drill_id} overlaps copper on "
                    f"{span.from_layer}..{span.to_layer}, but plating evidence "
                    "is unknown; no vertical electrical connection was created"
                ),
                source_path,
            )
        )


def reconstruct(
    source: str | Path,
    config: ReconstructionConfig | None = None,
) -> ReconstructionResult:
    """Reconstruct a directory, single CAM file, or ZIP manufacturing package."""
    cfg = config or ReconstructionConfig()

    with prepare_input(source) as prepared:
        board = BoardModel(
            metadata={
                "source_input": str(prepared.original),
                "input_kind": prepared.kind,
                "source_directory": str(prepared.root),
            }
        )
        files = discover_manufacturing_files(prepared.root)
        if not files:
            raise FileNotFoundError(
                f"no Gerber/Excellon manufacturing files found in {source}"
            )

        board.metadata["manufacturing_file_count"] = len(files)

        for item in files:
            if item.kind == "drill":
                result = ExcellonParser(strict=cfg.strict_parsing).parse(item.path)
                _apply_file_plating_hint(board, item, result.drills)
                board.drills.extend(result.drills)
                board.slots.extend(result.slots)
                board.routes.extend(result.routes)
                board.diagnostics.extend(result.diagnostics)
                continue

            layer = item.layer
            if layer is None:
                board.diagnostics.append(
                    ParseDiagnostic(
                        "warning",
                        "UNKNOWN_LAYER",
                        (
                            "Gerber file skipped because layer could not be "
                            "inferred from X2 attributes or filename"
                        ),
                        str(item.path),
                    )
                )
                continue

            result = GerberRS274XParser(
                layer,
                strict=cfg.strict_parsing,
            ).parse(item.path)
            board.tracks.extend(result.tracks)
            board.pads.extend(result.pads)
            board.regions.extend(result.regions)
            board.outline.extend(result.outline)
            board.diagnostics.extend(result.diagnostics)

        attach_drills(board, cfg.drill_attach_tolerance_mm)

        stackup = infer_stackup(board)
        via_spans = resolve_via_spans(
            board,
            stackup,
            cfg.drill_attach_tolerance_mm,
        )
        board.metadata["stackup"] = stackup.to_dict()
        board.metadata["via_spans"] = _serialize_via_spans(via_spans)
        _report_unproven_multilayer_spans(board, via_spans)

        graph = build_physical_graph(
            board,
            cfg.connectivity_tolerance_mm,
            via_spans=via_spans,
        )
        assign_physical_nets(board, graph)
        infer_component_hypotheses(board, cfg.component_pair_distance_mm)
        return ReconstructionResult(board, validate_board(board))
