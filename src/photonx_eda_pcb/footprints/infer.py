from .clustering import cluster_pads
from .matcher import match_signature
from .orientation import principal_orientation_deg
from .candidate import FootprintCandidate
from ..ids import stable_id


_X2_REFDES = "gerber_x2_component_refdes"
_X2_PIN = "gerber_x2_pin_number"
_X2_PIN_FUNCTION = "gerber_x2_pin_function"
_STEP_REPEAT = "gerber_step_repeat"


def _trusted_evidence_values(pad, kind):
    return tuple(
        sorted(
            {
                evidence.detail
                for evidence in pad.provenance.evidence
                if evidence.kind == kind and evidence.confidence == 1.0
            }
        )
    )


def _source_partition(pads):
    groups = {}
    conflicts = []
    remaining = []

    for pad in sorted(pads, key=lambda item: item.id):
        refdes_values = _trusted_evidence_values(pad, _X2_REFDES)
        if not refdes_values:
            remaining.append(pad)
            continue

        if len(refdes_values) != 1 or not refdes_values[0]:
            conflicts.append((pad, refdes_values))
            continue

        refdes = refdes_values[0]
        step_repeat = tuple(
            value
            for value in _trusted_evidence_values(pad, _STEP_REPEAT)
            if value
        )
        groups.setdefault((refdes, step_repeat), []).append(pad)

    return groups, conflicts, remaining


def _pin_evidence(pads):
    details = []
    for pad in pads:
        pin_numbers = tuple(
            value
            for value in _trusted_evidence_values(pad, _X2_PIN)
            if value
        )
        if len(pin_numbers) != 1:
            continue

        pin_functions = tuple(
            value
            for value in _trusted_evidence_values(pad, _X2_PIN_FUNCTION)
            if value
        )
        detail = f"{pad.id}={pin_numbers[0]}"
        if len(pin_functions) == 1:
            detail += f" ({pin_functions[0]})"
        details.append(detail)
    return details


def _matched_candidate(
    pads,
    *,
    candidate_id,
    reference=None,
    boundary_source="geometric_proximity",
    boundary_confidence=0.0,
    evidence_prefix=(),
):
    pads = sorted(pads, key=lambda item: item.id)
    match = match_signature(pads)
    evidence = list(evidence_prefix)
    evidence.append(
        f"matched {match['best']} from {len(pads)} pads"
    )
    return FootprintCandidate(
        candidate_id,
        [pad.id for pad in pads],
        match["best"],
        match["confidence"],
        principal_orientation_deg(pads),
        evidence,
        reference=reference,
        boundary_source=boundary_source,
        boundary_confidence=boundary_confidence,
    )


def infer_footprints(
    board,
    max_gap_mm=5.0,
    *,
    max_cluster_span_mm=None,
    backend="auto",
):
    out = []
    groups, conflicts, remaining = _source_partition(board.pads)

    for (refdes, step_repeat), members in sorted(
        groups.items(),
        key=lambda item: (item[0][0], item[0][1]),
    ):
        members = sorted(members, key=lambda item: item.id)
        pad_ids = [pad.id for pad in members]
        evidence = [
            f"Gerber X2 .P component reference: {refdes}",
            "source-proven footprint boundary; package/signature classification remains heuristic",
        ]
        evidence.extend(
            f"Gerber step-repeat instance: {detail}"
            for detail in step_repeat
        )
        pin_details = _pin_evidence(members)
        if pin_details:
            evidence.append("Gerber X2 .P pins: " + ", ".join(pin_details))

        out.append(
            _matched_candidate(
                members,
                candidate_id=stable_id(
                    "fp",
                    "gerber_x2_refdes",
                    refdes,
                    *step_repeat,
                    *pad_ids,
                ),
                reference=refdes,
                boundary_source="gerber_x2_component_refdes",
                boundary_confidence=1.0,
                evidence_prefix=evidence,
            )
        )

    for pad, refdes_values in conflicts:
        detail = ", ".join(repr(value) for value in refdes_values) or "<empty>"
        out.append(
            FootprintCandidate(
                stable_id(
                    "fp",
                    "gerber_x2_refdes_conflict",
                    pad.id,
                    *refdes_values,
                ),
                [pad.id],
                None,
                0.0,
                principal_orientation_deg([pad]),
                [
                    "conflicting or empty trusted Gerber X2 .P component "
                    f"reference evidence: {detail}",
                    "pad withheld from geometric footprint clustering",
                ],
                boundary_source="gerber_x2_refdes_conflict",
                boundary_confidence=0.0,
            )
        )

    for group in cluster_pads(
        remaining,
        max_gap_mm,
        max_cluster_span_mm=max_cluster_span_mm,
        backend=backend,
    ):
        group = sorted(group, key=lambda item: item.id)
        pad_ids = [pad.id for pad in group]
        out.append(
            _matched_candidate(
                group,
                candidate_id=stable_id("fp", "geometric_proximity", *pad_ids),
                boundary_source="geometric_proximity",
                boundary_confidence=0.0,
                evidence_prefix=(
                    "component boundary is a geometric proximity hypothesis only",
                ),
            )
        )

    return out
