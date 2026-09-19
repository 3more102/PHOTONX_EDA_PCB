from __future__ import annotations

from math import hypot

from ..ids import stable_id
from ..models import BoardModel, ComponentHypothesis
from ..spatial_connectivity.points import build_point_index, radius_queries


def _evidence_details(pad, kind: str) -> list[str]:
    return sorted(
        {
            evidence.detail
            for evidence in pad.provenance.evidence
            if evidence.kind == kind
        }
    )


def _source_component_hypotheses(pads):
    """Promote source-proven Gerber X2 TO.P identity before geometric inference."""

    groups = {}
    conflicts = []
    remaining = []

    for pad in sorted(pads, key=lambda item: item.id):
        refdes_values = _evidence_details(pad, "gerber_x2_component_refdes")
        if not refdes_values:
            remaining.append(pad)
            continue

        if len(refdes_values) != 1 or not refdes_values[0]:
            detail = ", ".join(repr(value) for value in refdes_values) or "<missing>"
            conflicts.append(
                ComponentHypothesis(
                    stable_id("cmp", "gerber_x2_conflict", pad.id),
                    [pad.id],
                    "gerber_x2_component_conflict",
                    0.0,
                    [f"conflicting or empty Gerber X2 component refdes evidence: {detail}"],
                )
            )
            continue

        refdes = refdes_values[0]
        step_repeat = tuple(_evidence_details(pad, "gerber_step_repeat"))
        groups.setdefault((refdes, step_repeat), []).append(pad)

    components = []
    for (refdes, step_repeat), members in sorted(
        groups.items(), key=lambda item: (item[0][0], item[0][1])
    ):
        pad_ids = sorted(pad.id for pad in members)
        ref_confidences = [
            evidence.confidence
            for pad in members
            for evidence in pad.provenance.evidence
            if evidence.kind == "gerber_x2_component_refdes"
            and evidence.detail == refdes
        ]
        confidence = min(ref_confidences) if ref_confidences else 1.0
        evidence_text = [f"Gerber X2 TO.P refdes {refdes}"]

        if step_repeat:
            evidence_text.extend(f"step-repeat {detail}" for detail in step_repeat)

        for pad in sorted(members, key=lambda item: item.id):
            pin_numbers = _evidence_details(pad, "gerber_x2_pin_number")
            pin_functions = _evidence_details(pad, "gerber_x2_pin_function")
            if len(pin_numbers) == 1:
                pin = pin_numbers[0] if pin_numbers[0] else "<empty>"
                detail = f"{pad.id}: pin {pin}"
                if len(pin_functions) == 1:
                    detail += f" ({pin_functions[0]})"
                evidence_text.append(detail)

        components.append(
            ComponentHypothesis(
                stable_id(
                    "cmp",
                    "gerber_x2",
                    refdes,
                    *step_repeat,
                    *pad_ids,
                ),
                pad_ids,
                "gerber_x2_component",
                confidence,
                evidence_text,
                reference=refdes,
            )
        )

    return [*components, *conflicts], remaining


def _make_pair(a, b, distance):
    both_drilled = a.drill is not None and b.drill is not None
    same_layer = a.layer == b.layer
    confidence = 0.35 + (0.15 if both_drilled else 0.0) + (0.10 if same_layer else 0.0)
    kind = (
        "two_pin_through_hole_candidate"
        if both_drilled
        else "two_pad_component_candidate"
    )
    evidence = [
        f"pad pitch {distance:.3f} mm",
        "both pads have drill evidence" if both_drilled else "no complete drill evidence",
        f"layers: {a.layer}, {b.layer}",
    ]
    return ComponentHypothesis(
        stable_id("cmp", a.id, b.id),
        sorted([a.id, b.id]),
        kind,
        confidence,
        evidence,
    )


def _infer_geometry_bruteforce(pads, max_pair_distance_mm):
    remaining = {pad.id: pad for pad in pads}
    result = []
    while remaining:
        a_id = sorted(remaining)[0]
        a = remaining.pop(a_id)
        nearest = None
        for b_id, b in remaining.items():
            distance = hypot(a.center.x - b.center.x, a.center.y - b.center.y)
            if distance <= max_pair_distance_mm and (
                nearest is None or (distance, b_id) < (nearest[0], nearest[1])
            ):
                nearest = (distance, b_id, b)
        if nearest is None:
            result.append(
                ComponentHypothesis(
                    stable_id("cmp", a_id),
                    [a_id],
                    "unresolved_pad",
                    0.15,
                    ["no nearby pad partner"],
                )
            )
            continue
        distance, b_id, b = nearest
        remaining.pop(b_id)
        result.append(_make_pair(a, b, distance))
    return result


def infer_component_hypotheses_bruteforce(
    board: BoardModel,
    max_pair_distance_mm: float = 4.0,
    *,
    use_source_evidence: bool = True,
) -> list[ComponentHypothesis]:
    pads = list(board.pads)
    source_components = []
    if use_source_evidence:
        source_components, pads = _source_component_hypotheses(pads)
    result = [*source_components, *_infer_geometry_bruteforce(pads, max_pair_distance_mm)]
    board.components = result
    return result


def infer_component_hypotheses(
    board: BoardModel,
    max_pair_distance_mm: float = 4.0,
    *,
    use_spatial_index: bool = True,
    cell_size_mm: float | None = None,
    backend: str = "auto",
    use_source_evidence: bool = True,
) -> list[ComponentHypothesis]:
    if not use_spatial_index:
        return infer_component_hypotheses_bruteforce(
            board,
            max_pair_distance_mm,
            use_source_evidence=use_source_evidence,
        )

    pads = list(board.pads)
    source_components = []
    if use_source_evidence:
        source_components, pads = _source_component_hypotheses(pads)

    by = {pad.id: pad for pad in pads}
    remaining = set(by)
    result = list(source_components)
    if not pads:
        board.components = result
        return result

    idx = build_point_index(
        ((pad.id, pad) for pad in pads),
        lambda pad: (pad.center.x, pad.center.y),
        float(cell_size_mm or max(1.0, max_pair_distance_mm)),
    )
    neighbor_lists = radius_queries(
        idx,
        (
            (pad.center.x, pad.center.y, max_pair_distance_mm)
            for pad in pads
        ),
        backend=backend,
    )
    neighbors = {
        pad.id: items
        for pad, items in zip(pads, neighbor_lists)
    }

    while remaining:
        a_id = min(remaining)
        remaining.remove(a_id)
        a = by[a_id]
        nearest = next(
            (
                (distance, b_id)
                for distance, b_id in neighbors[a_id]
                if b_id in remaining
            ),
            None,
        )
        if nearest is None:
            result.append(
                ComponentHypothesis(
                    stable_id("cmp", a_id),
                    [a_id],
                    "unresolved_pad",
                    0.15,
                    ["no nearby pad partner"],
                )
            )
            continue
        distance, b_id = nearest
        remaining.remove(b_id)
        result.append(_make_pair(a, by[b_id], distance))

    board.components = result
    return result
