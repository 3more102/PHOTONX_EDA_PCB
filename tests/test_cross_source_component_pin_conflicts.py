from photonx_eda_pcb.cross_source_validation import (
    component_pin_observations,
    find_component_pin_conflicts,
)
from photonx_eda_pcb.models import PadCandidate, Point
from photonx_eda_pcb.provenance import Evidence, SourceRef


def _pad(pid: str) -> PadCandidate:
    return PadCandidate(pid, Point(0.0, 0.0), 1.0, 1.0, "C", "F.Cu")


def _add(pad, kind, detail, path, line):
    pad.provenance.add_evidence(
        Evidence(kind, detail, 1.0, SourceRef(path, line=line))
    )


def test_component_pin_observations_preserve_source_and_confidence():
    pad = _pad("P1")
    _add(pad, "gerber_x2_component_refdes", "U1", "top.gtl", 12)
    _add(pad, "gerber_x2_pin_number", "7", "top.gtl", 12)
    pad.provenance.add_evidence(Evidence("unrelated", "ignored", 0.5))

    observations = component_pin_observations([pad])

    assert [(o.subject_id, o.field, o.value, o.source, o.confidence) for o in observations] == [
        ("P1", "component_refdes", "U1", "top.gtl:12", 1.0),
        ("P1", "pin_number", "7", "top.gtl:12", 1.0),
    ]


def test_component_pin_conflicts_are_scoped_to_same_physical_pad():
    first = _pad("P1")
    second = _pad("P2")
    _add(first, "gerber_x2_component_refdes", "U1", "a.gtl", 10)
    _add(second, "gerber_x2_component_refdes", "U2", "b.gtl", 20)

    assert find_component_pin_conflicts([first, second]) == []


def test_component_pin_conflicts_report_refdes_disagreement():
    pad = _pad("P1")
    _add(pad, "gerber_x2_component_refdes", "U1", "a.gtl", 10)
    _add(pad, "gerber_x2_component_refdes", "U2", "b.gtl", 20)

    assert find_component_pin_conflicts([pad]) == [
        {
            "subject_id": "P1",
            "field": "component_refdes",
            "sources": ["a.gtl:10", "b.gtl:20"],
            "values": ["'U1'", "'U2'"],
        }
    ]


def test_component_pin_conflicts_include_pin_number_and_function():
    pad = _pad("P9")
    _add(pad, "gerber_x2_pin_number", "", "a.gtl", 3)
    _add(pad, "gerber_x2_pin_number", "9", "b.gtl", 4)
    _add(pad, "gerber_x2_pin_function", "GND", "a.gtl", 3)
    _add(pad, "gerber_x2_pin_function", "VSS", "b.gtl", 4)

    conflicts = find_component_pin_conflicts([pad])

    assert [item["field"] for item in conflicts] == ["pin_number", "pin_function"]
    assert conflicts[0]["values"] == ["''", "'9'"]
    assert conflicts[1]["values"] == ["'GND'", "'VSS'"]


def test_repeated_identical_component_pin_evidence_is_not_a_conflict():
    pad = _pad("P1")
    _add(pad, "gerber_x2_component_refdes", "U1", "a.gtl", 10)
    _add(pad, "gerber_x2_component_refdes", "U1", "b.gtl", 20)

    assert find_component_pin_conflicts([pad]) == []
