from __future__ import annotations

from math import hypot

from ..ids import stable_id
from ..models import BoardModel, ComponentHypothesis
from ..spatial_connectivity.points import build_point_index, radius_queries


def _evidence_events(pad, kind: str):
    return [
        evidence
        for evidence in pad.provenance.evidence
        if evidence.kind == kind
    ]


def _trusted_detail(pad, kind: str) -> tuple[str, str | None]:
    events = _evidence_events(pad, kind)
    if not events:
        return "absent", None

    details = {event.detail for event in events if event.detail}
    trusted = {
        event.detail
        for event in events
        if event.confidence == 1.0 and event.detail
    }
    if len(details) == 1 and trusted == details:
        return "trusted", next(iter(trusted))
    return "ambiguous", None


def _optional_trusted_detail(pad, kind: str) -> tuple[str, str | None]:
    status, detail = _trusted_detail(pad, kind)
    if status == "absent":
        return "trusted", None
    return status, detail


def _ambiguous_source_pad(
    pad,
    refdes: str | None,
    reason: str,
) -> ComponentHypothesis:
    evidence = [reason]
    if refdes is not None:
        evidence.insert(0, f"Gerber X2 TO.P refdes {refdes}")
    return ComponentHypothesis(
        stable_id("cmp", "gerber_x2_ambiguous", pad.id),
        [pad.id],
        "gerber_x2_component_ambiguous",
        0.0,
        evidence,
        reference=refdes,
    )


def _source_component_hypotheses(pads):
    groups: dict[tuple[str, str | None], list[object]] = {}
    review: list[ComponentHypothesis] = []
    remaining = []

    for pad in sorted(pads, key=lambda item: item.id):
        ref_status, refdes = _trusted_detail(
            pad,
            "gerber_x2_component_refdes",
        )
        if ref_status == "absent":
            remaining.append(pad)
            continue
        if ref_status != "trusted" or refdes is None:
            review.append(
                _ambiguous_source_pad(
                    pad,
                    None,
                    (
                        "conflicting, empty, or non-proven Gerber X2 "
                        "component refdes evidence"
                    ),
                )
            )
            continue

        repeat_status, repeat_instance = _optional_trusted_detail(
            pad,
            "gerber_step_repeat",
        )
        if repeat_status != "trusted":
            review.append(
                _ambiguous_source_pad(
                    pad,
                    refdes,
                    "ambiguous Gerber step-repeat instance evidence",
                )
            )
            continue

        groups.setdefault((refdes, repeat_instance), []).append(pad)

    components: list[ComponentHypothesis] = []
    for (refdes, repeat_instance), members in sorted(
        groups.items(),
        key=lambda item: (item[0][0], item[0][1] or ""),
    ):
        pins: list[tuple[object, str]] = []
        ambiguous_pin = False
        for pad in members:
            pin_status, pin_number = _trusted_detail(
                pad,
                "gerber_x2_pin_number",
            )
            if pin_status != "trusted" or pin_number is None:
                ambiguous_pin = True
                break
            pins.append((pad, pin_number))

        pin_numbers = [pin_number for _, pin_number in pins]
        repeated_pin = len(pin_numbers) != len(set(pin_numbers))
        if ambiguous_pin or repeated_pin:
            if repeated_pin and repeat_instance is None:
                reason = (
                    "repeated Gerber X2 pin numbers for one refdes without "
                    "explicit step-repeat instance evidence; possible expanded "
                    "panel copies"
                )
            elif repeated_pin:
                reason = (
                    "repeated Gerber X2 pin numbers inside one explicit "
                    "step-repeat instance"
                )
            else:
                reason = (
                    "missing, conflicting, or non-proven Gerber X2 pin evidence"
                )
            review.extend(
                _ambiguous_source_pad(pad, refdes, reason)
                for pad in members
            )
            continue

        pad_ids = sorted(pad.id for pad in members)
        evidence_text = [f"Gerber X2 TO.P refdes {refdes}"]
        if repeat_instance is not None:
            evidence_text.append(f"step-repeat {repeat_instance}")

        pin_by_id = {pad.id: pin_number for pad, pin_number in pins}
        for pad in sorted(members, key=lambda item: item.id):
            detail = f"{pad.id}: pin {pin_by_id[pad.id]}"
            function_status, pin_function = _optional_trusted_detail(
                pad,
                "gerber_x2_pin_function",
            )
            if function_status == "trusted" and pin_function is not None:
                detail += f" ({pin_function})"
            elif function_status == "ambiguous":
                detail += " (pin function ambiguous)"
            evidence_text.append(detail)

        components.append(
            ComponentHypothesis(
                stable_id(
                    "cmp",
                    "gerber_x2",
                    refdes,
                    repeat_instance or "",
                    *pad_ids,
                ),
                pad_ids,
                "gerber_x2_component",
                1.0,
                evidence_text,
                reference=refdes,
            )
        )

    return [*components, *review], remaining


def _make_pair(a, b, distance):
    both_drilled = a.drill is not None and b.drill is not None
    same_layer = a.layer == b.layer
    confidence = (
        0.35
        + (0.15 if both_drilled else 0.0)
        + (0.10 if same_layer else 0.0)
    )
    kind = (
        "two_pin_through_hole_candidate"
        if both_drilled
        else "two_pad_component_candidate"
    )
    evidence = [
        f"pad pitch {distance:.3f} mm",
        (
            "both pads have drill evidence"
            if both_drilled
            else "no complete drill evidence"
        ),
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
            distance = hypot(
                a.center.x - b.center.x,
                a.center.y - b.center.y,
            )
            if distance <= max_pair_distance_mm and (
                nearest is None
                or (distance, b_id) < (nearest[0], nearest[1])
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
    source_components: list[ComponentHypothesis] = []
    if use_source_evidence:
        source_components, pads = _source_component_hypotheses(pads)

    result = [
        *source_components,
        *_infer_geometry_bruteforce(pads, max_pair_distance_mm),
    ]
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
    source_components: list[ComponentHypothesis] = []
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
