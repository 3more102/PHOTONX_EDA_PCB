from __future__ import annotations

from math import hypot

from ..ids import stable_id
from ..models import BoardModel, ComponentHypothesis
from ..spatial_connectivity.points import build_point_index, radius_queries


_X2_REFDES = "gerber_x2_component_refdes"
_X2_PIN = "gerber_x2_pin_number"
_X2_PIN_FUNCTION = "gerber_x2_pin_function"
_STEP_REPEAT = "gerber_step_repeat"


def _evidence_events(pad, kind: str):
    return [
        evidence
        for evidence in pad.provenance.evidence
        if evidence.kind == kind
    ]


def _trusted_evidence_values(pad, kind: str) -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                evidence.detail
                for evidence in _evidence_events(pad, kind)
                if evidence.confidence == 1.0
            }
        )
    )


def _source_identity_conflict(pad, refdes_values, reason: str):
    detail = ", ".join(repr(value) for value in refdes_values) or "<empty>"
    return ComponentHypothesis(
        stable_id(
            "cmp",
            "gerber_x2_refdes_conflict",
            pad.id,
            *refdes_values,
            reason,
        ),
        [pad.id],
        "gerber_x2_component_conflict",
        0.0,
        [
            reason,
            f"Gerber X2 component reference evidence: {detail}",
        ],
    )


def _source_component_hypotheses(pads):
    """Use only source-proven X2 identity before geometric component guesses."""

    groups = {}
    conflicts = []
    remaining = []

    for pad in sorted(pads, key=lambda item: item.id):
        refdes_events = _evidence_events(pad, _X2_REFDES)
        if not refdes_events:
            remaining.append(pad)
            continue

        refdes_values = _trusted_evidence_values(pad, _X2_REFDES)
        all_refdes_values = tuple(
            sorted({event.detail for event in refdes_events})
        )
        fully_trusted = all(
            event.confidence == 1.0
            for event in refdes_events
        )

        if (
            not fully_trusted
            or len(refdes_values) != 1
            or len(all_refdes_values) != 1
            or not refdes_values[0]
        ):
            conflicts.append(
                _source_identity_conflict(
                    pad,
                    all_refdes_values,
                    (
                        "conflicting, empty, or non-proven trusted Gerber X2 "
                        ".P component reference evidence; pad excluded from "
                        "geometric reassignment"
                    ),
                )
            )
            continue

        refdes = refdes_values[0]
        step_repeat_events = _evidence_events(pad, _STEP_REPEAT)
        step_repeat = tuple(
            value
            for value in _trusted_evidence_values(pad, _STEP_REPEAT)
            if value
        )
        if step_repeat_events and (
            any(event.confidence != 1.0 for event in step_repeat_events)
            or len(step_repeat) != 1
        ):
            conflicts.append(
                _source_identity_conflict(
                    pad,
                    (refdes,),
                    (
                        "ambiguous Gerber step-repeat instance evidence; "
                        "pad excluded from geometric reassignment"
                    ),
                )
            )
            continue

        groups.setdefault((refdes, step_repeat), []).append(pad)

    components = []
    for (refdes, step_repeat), members in sorted(
        groups.items(),
        key=lambda item: (item[0][0], item[0][1]),
    ):
        members = sorted(members, key=lambda item: item.id)

        trusted_pins = []
        for pad in members:
            pin_numbers = tuple(
                value
                for value in _trusted_evidence_values(pad, _X2_PIN)
                if value
            )
            if len(pin_numbers) == 1:
                trusted_pins.append((pad.id, pin_numbers[0]))

        pin_numbers = [pin for _, pin in trusted_pins]
        duplicate_pins = sorted(
            {
                pin
                for pin in pin_numbers
                if pin_numbers.count(pin) > 1
            }
        )
        if duplicate_pins:
            reason = (
                "repeated trusted Gerber X2 pin numbers within one component "
                "identity group; possible expanded panel copies or split-pad "
                "identity ambiguity, so grouping fails closed"
            )
            for pad in members:
                conflicts.append(
                    _source_identity_conflict(
                        pad,
                        (refdes,),
                        reason + f": {', '.join(duplicate_pins)}",
                    )
                )
            continue

        pad_ids = [pad.id for pad in members]
        evidence = [
            f"Gerber X2 .P component reference: {refdes}",
            f"source-proven pad candidates: {len(pad_ids)}",
        ]

        if step_repeat:
            evidence.extend(
                f"Gerber step-repeat instance: {detail}"
                for detail in step_repeat
            )

        pin_details = []
        for pad in members:
            pin_numbers = tuple(
                value
                for value in _trusted_evidence_values(pad, _X2_PIN)
                if value
            )
            pin_functions = tuple(
                value
                for value in _trusted_evidence_values(
                    pad,
                    _X2_PIN_FUNCTION,
                )
                if value
            )
            if len(pin_numbers) != 1:
                continue

            detail = f"{pad.id}={pin_numbers[0]}"
            if len(pin_functions) == 1:
                detail += f" ({pin_functions[0]})"
            pin_details.append(detail)

        if pin_details:
            evidence.append(
                "Gerber X2 .P pins: " + ", ".join(pin_details)
            )

        components.append(
            ComponentHypothesis(
                stable_id(
                    "cmp",
                    "gerber_x2_refdes",
                    refdes,
                    *step_repeat,
                    *pad_ids,
                ),
                pad_ids,
                "gerber_x2_component",
                1.0,
                evidence,
                reference=refdes,
            )
        )

    return [*components, *conflicts], remaining


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


def infer_component_hypotheses_bruteforce(
    board: BoardModel,
    max_pair_distance_mm: float = 4.0,
) -> list[ComponentHypothesis]:
    source_components, remaining_pads = _source_component_hypotheses(
        board.pads
    )
    remaining = {pad.id: pad for pad in remaining_pads}
    result = list(source_components)

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

    board.components = result
    return result


def infer_component_hypotheses(
    board: BoardModel,
    max_pair_distance_mm: float = 4.0,
    *,
    use_spatial_index: bool = True,
    cell_size_mm: float | None = None,
    backend: str = "auto",
) -> list[ComponentHypothesis]:
    if not use_spatial_index:
        return infer_component_hypotheses_bruteforce(
            board,
            max_pair_distance_mm,
        )

    source_components, pads = _source_component_hypotheses(board.pads)
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
