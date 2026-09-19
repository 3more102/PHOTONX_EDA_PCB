from __future__ import annotations

from collections.abc import Iterable

from .conflicts import find_conflicts
from .model import SourceObservation

_EVIDENCE_FIELDS = {
    "gerber_x2_component_refdes": "component_refdes",
    "gerber_x2_pin_number": "pin_number",
    "gerber_x2_pin_function": "pin_function",
}


def _source_name(source) -> str:
    if source is None:
        return "<unknown>"
    if source.line is None:
        return source.path
    return f"{source.path}:{source.line}"


def component_pin_observations(pads: Iterable[object]) -> list[SourceObservation]:
    """Convert source-proven component-pin pad evidence into observations.

    The observation subject is the physical pad ID.  Evidence attached to
    different pads is intentionally kept separate because repeated component
    pin numbers can be legitimate for some package constructions; this helper
    only exposes disagreements about the same recovered physical pad.
    """
    out: list[SourceObservation] = []
    for pad in sorted(pads, key=lambda item: str(item.id)):
        provenance = getattr(pad, "provenance", None)
        for evidence in getattr(provenance, "evidence", ()):
            field = _EVIDENCE_FIELDS.get(evidence.kind)
            if field is None:
                continue
            out.append(
                SourceObservation(
                    source=_source_name(evidence.source),
                    subject_id=str(pad.id),
                    field=field,
                    value=evidence.detail,
                    confidence=evidence.confidence,
                )
            )
    return out


def find_component_pin_conflicts(pads: Iterable[object]) -> list[dict[str, object]]:
    """Report contradictory X2 component-pin evidence on the same pad."""
    return find_conflicts(component_pin_observations(pads))
