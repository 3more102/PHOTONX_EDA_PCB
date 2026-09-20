from __future__ import annotations

from math import hypot

from ..ids import stable_id
from ..footprints.matcher import match_signature
from ..models import BoardModel, ComponentHypothesis
from ..spatial_connectivity.points import build_point_index, radius_queries


_X2_REFDES = "gerber_x2_component_refdes"
_X2_PIN = "gerber_x2_pin_number"
_X2_PIN_FUNCTION = "gerber_x2_pin_function"
_STEP_REPEAT = "gerber_step_repeat"


def _package_hint_from_pads(pads):
    match = match_signature(pads)
    if match["best"] is not None:
        return match["best"], [
            "pad-topology package hint: "
            f'{match["best"]} '
            f'(score={match["confidence"]:.3f}, margin={match["margin"]:.3f})'
        ]

    if match["ambiguous"]:
        top = ", ".join(
            f"{name}={score:.3f}"
            for score, name in match["ranking"][:2]
        )
        return None, [
            "pad-topology package hint unresolved: ambiguous "
            f"({top})"
        ]

    candidate = match.get("candidate")
    score = match.get("candidate_confidence", 0.0)
    if candidate and score > 0.0:
        return None, [
            "pad-topology package hint unresolved: "
            f"{candidate} score {score:.3f} below acceptance threshold"
        ]
    return None, ["pad-topology package hint unresolved: no supported topology"]


def _trusted_evidence_values(pad, kind: str) -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                evidence.detail
                for evidence in pad.provenance.evidence
                if evidence.kind == kind and evidence.confidence == 1.0
            }
        )
    )


def _source_component_hypotheses(pads):
    """Use only source-proven X2 identity before geometric component guesses."""

    groups = {}
    conflicts = []
    remaining = []

    for pad in sorted(pads, key=lambda item: item.id):
        refdes_values = _trusted_evidence_values(pad, _X2_REFDES)
        if not refdes_values:
            remaining.append(pad)
            continue

        if len(refdes_values) != 1 or not refdes_values[0]:
            detail = ", ".join(repr(value) for value in refdes_values) or "<empty>"
            conflicts.append(
                ComponentHypothesis(
                    stable_id(
                        "cmp",
                        "gerber_x2_refdes_conflict",
                        pad.id,
                        *refdes_values,
                    ),
                    [pad.id],
                    "gerber_x2_component_conflict",
                    0.0,
                    [
                        "conflicting or empty trusted Gerber X2 .P component "
                        f"reference evidence: {detail}"
                    ],
                )
            )
            continue

        refdes = refdes_values[0]
        step_repeat = tuple(
            value
            for value in _trusted_evidence_values(pad, _STEP_REPEAT)
            if value
        )
        groups.setdefault((refdes, step_repeat), []).append(pad)

    components = []
    for (refdes, step_repeat), members in sorted(
        groups.items(),
        key=lambda item: (item[0][0], item[0][1]),
    ):
        members = sorted(members, key=lambda item: item.id)
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

        source_pin_map = {}
        source_pin_functions = {}
        pin_details = []
        unresolved_pin_pads = []
        unresolved_function_pads = []
        for pad in members:
            pin_numbers = tuple(
                value
                for value in _trusted_evidence_values(pad, _X2_PIN)
                if value
            )
            pin_functions = tuple(
                value
                for value in _trusted_evidence_values(pad, _X2_PIN_FUNCTION)
                if value
            )

            if len(pin_numbers) != 1:
                unresolved_pin_pads.append(pad.id)
                continue

            pin_number = pin_numbers[0]
            source_pin_map[pad.id] = pin_number
            detail = f"{pad.id}={pin_number}"

            if len(pin_functions) == 1:
                pin_function = pin_functions[0]
                source_pin_functions[pad.id] = pin_function
                detail += f" ({pin_function})"
            elif len(pin_functions) > 1:
                unresolved_function_pads.append(pad.id)

            pin_details.append(detail)

        if pin_details:
            evidence.append("Gerber X2 .P pins: " + ", ".join(pin_details))
        if unresolved_pin_pads:
            evidence.append(
                "Gerber X2 .P pin identity unresolved for pads: "
                + ", ".join(unresolved_pin_pads)
            )
        if unresolved_function_pads:
            evidence.append(
                "Gerber X2 .P pin function unresolved for pads: "
                + ", ".join(unresolved_function_pads)
            )

        package_hint, package_evidence = _package_hint_from_pads(members)
        evidence.extend(package_evidence)

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
                package_hint=package_hint,
                source_pin_map=source_pin_map,
                source_pin_functions=source_pin_functions,
            )
        )

    return [*components, *conflicts], remaining


def _make_pair(a, b, distance):
    both_drilled = a.drill is not None and b.drill is not None
    package_hint, package_evidence = _package_hint_from_pads([a, b])
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
        *package_evidence,
    ]
    return ComponentHypothesis(
        stable_id("cmp", a.id, b.id),
        sorted([a.id, b.id]),
        kind,
        confidence,
        evidence,
        package_hint=package_hint,
    )


def infer_component_hypotheses_bruteforce(
    board: BoardModel,
    max_pair_distance_mm: float = 4.0,
) -> list[ComponentHypothesis]:
    source_components, remaining_pads = _source_component_hypotheses(board.pads)
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
