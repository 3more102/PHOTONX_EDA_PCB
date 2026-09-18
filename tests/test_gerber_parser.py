from pathlib import Path

import pytest

from photonx_eda_pcb.errors import UnsupportedFeatureError
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser

FIX = Path(__file__).parent / "fixtures" / "led"


def test_copper_parser_extracts_evidence_objects():
    result = GerberRS274XParser("F.Cu").parse(FIX / "copper.gbr")
    assert len(result.pads) == 6
    assert len(result.tracks) == 4
    assert all(p.provenance.sources for p in result.pads)
    assert all(t.provenance.sources for t in result.tracks)


def test_outline_parser_keeps_outline_separate():
    result = GerberRS274XParser("Edge.Cuts").parse(FIX / "outline.gbr")
    assert len(result.outline) == 4
    assert not result.tracks


def test_unsupported_arc_is_not_silently_ignored(tmp_path):
    p = tmp_path / "arc.gbr"
    p.write_text(
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%ADD10C,0.2*%\n"
        "D10*\n"
        "G02X010000Y010000I000500J000000D01*\n"
        "M02*\n"
    )
    with pytest.raises(UnsupportedFeatureError):
        GerberRS274XParser("F.Cu", strict=True).parse(p)


def test_step_repeat_expands_flash_geometry_with_provenance(tmp_path):
    p = tmp_path / "panel_flash.gbr"
    p.write_text(
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%ADD10C,1.0*%\n"
        "D10*\n"
        "%SRX2Y2I10.0J5.0*%\n"
        "X010000Y020000D03*\n"
        "%SR*%\n"
        "M02*\n"
    )

    result = GerberRS274XParser("F.Cu").parse(p)

    assert [(pad.center.x, pad.center.y) for pad in result.pads] == [
        (1.0, 2.0),
        (11.0, 2.0),
        (1.0, 7.0),
        (11.0, 7.0),
    ]
    assert len({pad.id for pad in result.pads}) == 4
    assert all(
        pad.provenance.sources[0].raw == "X010000Y020000D03*"
        for pad in result.pads
    )
    assert all(
        any(ev.kind == "gerber_step_repeat" for ev in pad.provenance.evidence)
        for pad in result.pads
    )


def test_step_repeat_expands_draws_and_bare_sr_terminates_repeat(tmp_path):
    p = tmp_path / "panel_tracks.gbr"
    p.write_text(
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%ADD10C,0.2*%\n"
        "D10*\n"
        "X010000Y010000D02*\n"
        "%SRX2Y1I4.0J0.0*%\n"
        "X030000Y010000D01*\n"
        "%SR*%\n"
        "X050000Y010000D01*\n"
        "M02*\n"
    )

    result = GerberRS274XParser("F.Cu").parse(p)

    assert len(result.tracks) == 3
    assert [
        (track.start.x, track.start.y, track.end.x, track.end.y)
        for track in result.tracks
    ] == [
        (1.0, 1.0, 3.0, 1.0),
        (5.0, 1.0, 7.0, 1.0),
        (3.0, 1.0, 5.0, 1.0),
    ]
    assert any(
        ev.kind == "gerber_step_repeat"
        for ev in result.tracks[0].provenance.evidence
    )
    assert not result.tracks[-1].provenance.evidence


def test_step_repeat_step_distance_uses_active_gerber_units(tmp_path):
    p = tmp_path / "inch_panel.gbr"
    p.write_text(
        "%FSLAX24Y24*%\n"
        "%MOIN*%\n"
        "%ADD10C,0.040*%\n"
        "D10*\n"
        "%SRX2Y1I1.0J0.0*%\n"
        "X010000Y010000D03*\n"
        "%SR*%\n"
        "M02*\n"
    )

    result = GerberRS274XParser("F.Cu").parse(p)

    assert [pad.center.x for pad in result.pads] == pytest.approx([25.4, 50.8])
    assert [pad.center.y for pad in result.pads] == pytest.approx([25.4, 25.4])
