from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
import re

from .config import ReconstructionConfig
from .connectivity import attach_drills, build_physical_graph, assign_physical_nets
from .inference import infer_component_hypotheses
from .input_package import prepare_input
from .models import BoardModel, ParseDiagnostic
from .parsers import discover_manufacturing_files, GerberRS274XParser, ExcellonParser
from .stackup import infer_stackup
from .validation import ValidationReport, validate_board
from .via_span import resolve_via_spans
from .x2_span import mapped_x2_span_layers


_X2_COPPER_ORDINAL = re.compile(r"^L([1-9][0-9]*)$", re.IGNORECASE)
_X2_COPPER_SIDES = {"top", "inr", "bot"}


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
            "layer_ids": list(span.layer_ids),
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


def _canonical_x2_copper_layer(ordinal: int, side: str) -> str:
    if side == "top":
        return "F.Cu"
    if side == "bot":
        return "B.Cu"
    return f"In{ordinal - 1}.Cu"


def _apply_x2_copper_stackup_evidence(board: BoardModel, files) -> None:
    declarations = []
    issues = []

    for item in files:
        fields = tuple(getattr(item, "x2_file_function", ()) or ())
        if not fields or str(fields[0]).lower() != "copper":
            continue

        declaration = {
            "path": str(item.path),
            "layer": item.layer,
            "fields": list(fields),
        }

        if len(fields) < 3:
            issues.append(
                f"{item.path.name}: Copper FileFunction requires L<p> and Top/Inr/Bot"
            )
            declarations.append(declaration)
            continue

        ordinal_match = _X2_COPPER_ORDINAL.fullmatch(str(fields[1]))
        side = str(fields[2]).lower()
        if ordinal_match is None:
            issues.append(
                f"{item.path.name}: invalid copper layer ordinal {fields[1]!r}"
            )
            declarations.append(declaration)
            continue
        if side not in _X2_COPPER_SIDES:
            issues.append(
                f"{item.path.name}: invalid copper layer side {fields[2]!r}"
            )
            declarations.append(declaration)
            continue

        ordinal = int(ordinal_match.group(1))
        canonical_layer = _canonical_x2_copper_layer(ordinal, side)
        declaration.update(
            {
                "ordinal": ordinal,
                "side": side,
                "canonical_layer": canonical_layer,
            }
        )
        declarations.append(declaration)

        if side == "top" and ordinal != 1:
            issues.append(
                f"{item.path.name}: X2 top copper must be L1, observed L{ordinal}"
            )
        if side in {"inr", "bot"} and ordinal == 1:
            issues.append(
                f"{item.path.name}: L1 cannot be declared as {side}"
            )
        if item.layer is not None and item.layer != canonical_layer:
            issues.append(
                (
                    f"{item.path.name}: inferred layer {item.layer} conflicts with "
                    f"X2 {canonical_layer}"
                )
            )

    if not declarations:
        return

    valid = [item for item in declarations if "ordinal" in item]
    bottom_ordinals = {
        int(item["ordinal"])
        for item in valid
        if item.get("side") == "bot"
    }

    if len(bottom_ordinals) > 1:
        values = ", ".join(f"L{value}" for value in sorted(bottom_ordinals))
        issues.append(f"conflicting X2 bottom copper ordinals: {values}")

    by_ordinal = {}
    by_layer = {}
    for item in valid:
        ordinal = int(item["ordinal"])
        layer = str(item["canonical_layer"])
        signature = (str(item["side"]), layer)

        prior = by_ordinal.get(ordinal)
        if prior is not None and prior != signature:
            issues.append(
                f"X2 copper L{ordinal} has conflicting side/layer declarations"
            )
        else:
            by_ordinal[ordinal] = signature

        prior_ordinal = by_layer.get(layer)
        if prior_ordinal is not None and prior_ordinal != ordinal:
            issues.append(
                f"X2 copper layer {layer} is assigned to multiple ordinals"
            )
        else:
            by_layer[layer] = ordinal

    total = next(iter(bottom_ordinals)) if len(bottom_ordinals) == 1 else None
    if total is not None:
        if total < 2:
            issues.append("X2 bottom copper ordinal must be at least L2")
        for item in valid:
            ordinal = int(item["ordinal"])
            side = str(item["side"])
            if ordinal > total:
                issues.append(
                    f"{item['path']}: L{ordinal} exceeds bottom ordinal L{total}"
                )
                continue
            expected_side = (
                "top"
                if ordinal == 1
                else ("bot" if ordinal == total else "inr")
            )
            if side != expected_side:
                issues.append(
                    (
                        f"{item['path']}: L{ordinal} must be {expected_side} "
                        f"when bottom is L{total}, observed {side}"
                    )
                )

    unique_issues = list(dict.fromkeys(issues))
    metadata = {
        "source": "gerber_x2_file_function",
        "declarations": declarations,
    }

    if unique_issues:
        metadata["status"] = "conflict"
        metadata["issues"] = unique_issues
        board.metadata["x2_copper_stackup"] = metadata
        board.diagnostics.append(
            ParseDiagnostic(
                "warning",
                "X2_COPPER_STACKUP_CONFLICT",
                "; ".join(unique_issues),
                str(board.metadata.get("source_input", "")),
            )
        )
        return

    if total is None:
        metadata["status"] = "partial"
        board.metadata["x2_copper_stackup"] = metadata
        return

    layers = ["F.Cu"]
    layers.extend(f"In{index}.Cu" for index in range(1, total - 1))
    layers.append("B.Cu")
    metadata.update(
        {
            "status": "declared",
            "declared_copper_count": total,
            "layers": layers,
        }
    )
    board.metadata["x2_copper_stackup"] = metadata


def _x2_span_source(feature):
    provenance = getattr(feature, "provenance", None)
    for evidence in getattr(provenance, "evidence", ()):
        if getattr(evidence, "kind", None) != "excellon_x2_file_span":
            continue
        source = getattr(evidence, "source", None)
        if source is not None:
            return source
    sources = getattr(provenance, "sources", ())
    return sources[0] if sources else None


def _resolve_explicit_x2_feature_spans(board: BoardModel, stackup) -> None:
    families = (
        ("slots", "slot", "X2_SLOT_SPAN_UNRESOLVED"),
        ("routes", "route", "X2_ROUTE_SPAN_UNRESOLVED"),
    )
    default_path = str(board.metadata.get("source_input", ""))

    for collection_name, feature_kind, diagnostic_code in families:
        resolved = []
        for feature in getattr(board, collection_name, ()):
            mapped_span, span_issue = mapped_x2_span_layers(
                board,
                stackup,
                feature,
            )
            if mapped_span is None:
                resolved.append(feature)
                continue

            if span_issue is not None or len(mapped_span) < 2:
                resolved.append(
                    replace(
                        feature,
                        layer_span=None,
                        span_proven=False,
                    )
                )
                source = _x2_span_source(feature)
                detail = span_issue or "mapped X2 span contains fewer than two copper layers"
                board.diagnostics.append(
                    ParseDiagnostic(
                        "warning",
                        diagnostic_code,
                        f"{feature.id}: X2 span unresolved: {detail}",
                        default_path if source is None else str(source.path),
                        None if source is None else source.line,
                    )
                )
                continue

            resolved.append(
                replace(
                    feature,
                    layer_span=(mapped_span[0], mapped_span[-1]),
                    span_proven=True,
                )
            )

        setattr(board, collection_name, resolved)


def _report_unresolved_x2_drill_spans(board: BoardModel, spans) -> None:
    source_path = str(board.metadata.get("source_input", ""))
    for span in spans:
        unresolved = [
            item
            for item in span.evidence
            if str(item).startswith("X2 span unresolved:")
        ]
        if not unresolved:
            continue
        board.diagnostics.append(
            ParseDiagnostic(
                "warning",
                "X2_DRILL_SPAN_UNRESOLVED",
                f"{span.drill_id}: {unresolved[0]}",
                source_path,
            )
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
        _apply_x2_copper_stackup_evidence(board, files)

        for item in files:
            if getattr(item, "x2_file_function_conflict", False):
                board.diagnostics.append(
                    ParseDiagnostic(
                        "warning",
                        "X2_FILE_FUNCTION_REDEFINED",
                        (
                            "Gerber file skipped because .FileFunction is a "
                            "unique immutable file attribute and was declared "
                            "more than once"
                        ),
                        str(item.path),
                    )
                )
                continue

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
        _resolve_explicit_x2_feature_spans(board, stackup)
        via_spans = resolve_via_spans(
            board,
            stackup,
            cfg.drill_attach_tolerance_mm,
        )
        board.metadata["stackup"] = stackup.to_dict()
        board.metadata["via_spans"] = _serialize_via_spans(via_spans)
        _report_unresolved_x2_drill_spans(board, via_spans)
        _report_unproven_multilayer_spans(board, via_spans)

        graph = build_physical_graph(
            board,
            cfg.connectivity_tolerance_mm,
            via_spans=via_spans,
        )
        assign_physical_nets(board, graph)
        infer_component_hypotheses(board, cfg.component_pair_distance_mm)
        return ReconstructionResult(board, validate_board(board))
