from types import SimpleNamespace

from photonx_eda_pcb.ipc356.alignment import (
    infer_translation_alignment,
    translate_records,
)
from photonx_eda_pcb.ipc356.map_records import align_and_map_records_to_pads
from photonx_eda_pcb.ipc356.model import Ipc356Record


def _pad(pad_id, x, y):
    return SimpleNamespace(id=pad_id, center=SimpleNamespace(x=x, y=y))


def test_infers_translation_from_multiple_consistent_anchors():
    records = [
        Ipc356Record("317", "GND", "U1", "1", 0.0, 0.0, "TOP", ""),
        Ipc356Record("317", "VCC", "U1", "2", 10.0, 0.0, "TOP", ""),
        Ipc356Record("317", "SIG", "U2", "1", 0.0, 5.0, "TOP", ""),
    ]
    pads = [
        _pad("P1", 1.25, -0.75),
        _pad("P2", 11.25, -0.75),
        _pad("P3", 1.25, 4.25),
    ]

    alignment = infer_translation_alignment(records, pads, tolerance_mm=0.05)

    assert alignment is not None
    assert alignment.dx_mm == 1.25
    assert alignment.dy_mm == -0.75
    assert alignment.matched_records == 3
    assert alignment.rms_residual_mm == 0.0


def test_alignment_is_fail_closed_when_periodic_geometry_is_ambiguous():
    records = [
        Ipc356Record("317", "A", None, None, 0.0, 0.0, None, ""),
        Ipc356Record("317", "B", None, None, 10.0, 0.0, None, ""),
    ]
    pads = [
        _pad("P1", 1.0, 0.0),
        _pad("P2", 11.0, 0.0),
        _pad("P3", 21.0, 0.0),
    ]

    assert infer_translation_alignment(records, pads, tolerance_mm=0.01) is None


def test_alignment_requires_multiple_anchors():
    records = [Ipc356Record("317", "A", None, None, 0.0, 0.0, None, "")]
    pads = [_pad("P1", 2.0, 3.0)]

    assert infer_translation_alignment(records, pads, tolerance_mm=0.01) is None


def test_align_and_map_uses_proven_translation_without_mutating_source_records():
    records = [
        Ipc356Record("317", "GND", "U1", "1", 0.0, 0.0, "TOP", ""),
        Ipc356Record("317", "VCC", "U1", "2", 10.0, 0.0, "TOP", ""),
        Ipc356Record("317", None, None, None, None, None, None, ""),
    ]
    pads = [_pad("P1", 2.0, -1.0), _pad("P2", 12.0, -1.0)]

    evidence, unmatched, alignment = align_and_map_records_to_pads(
        records, pads, tolerance_mm=0.05
    )

    assert alignment is not None
    assert (alignment.dx_mm, alignment.dy_mm) == (2.0, -1.0)
    assert [item.pad_id for item in evidence] == ["P1", "P2"]
    assert [item.net_name for item in evidence] == ["GND", "VCC"]
    assert len(unmatched) == 1
    assert records[0].x == 0.0 and records[0].y == 0.0

    translated = translate_records(records, alignment)
    assert translated[0].x == 2.0 and translated[0].y == -1.0
    assert translated[2] is records[2]
