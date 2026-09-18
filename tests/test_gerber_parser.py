from pathlib import Path

import pytest

from photonx_eda_pcb.errors import ParseError, UnsupportedFeatureError
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



def test_g75_ccw_arc_is_tessellated_with_explicit_evidence(tmp_path):
    p = tmp_path / "g75_ccw.gbr"
    p.write_text(
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "G75*\n"
        "G03*\n"
        "X010000Y000000D02*\n"
        "X000000Y010000I-010000J000000D01*\n"
        "M02*\n"
    )

    result = GerberRS274XParser("F.Cu").parse(p)

    assert len(result.tracks) > 1
    assert result.tracks[0].start.x == pytest.approx(1.0)
    assert result.tracks[0].start.y == pytest.approx(0.0)
    assert result.tracks[-1].end.x == pytest.approx(0.0)
    assert result.tracks[-1].end.y == pytest.approx(1.0)
    assert all(track.width == pytest.approx(0.2) for track in result.tracks)
    assert all(
        any(ev.kind == "gerber_arc_tessellation" for ev in track.provenance.evidence)
        for track in result.tracks
    )
    assert all(
        track.provenance.sources[0].raw
        == "X000000Y010000I-010000J000000D01*"
        for track in result.tracks
    )


def test_g01_resets_modal_arc_interpolation(tmp_path):
    p = tmp_path / "arc_then_line.gbr"
    p.write_text(
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "G75*\n"
        "G03*\n"
        "X010000Y000000D02*\n"
        "X000000Y010000I-010000J000000D01*\n"
        "G01*\n"
        "X000000Y020000D01*\n"
        "M02*\n"
    )

    result = GerberRS274XParser("F.Cu").parse(p)

    assert len(result.tracks) > 2
    assert result.tracks[-1].start.x == pytest.approx(0.0)
    assert result.tracks[-1].start.y == pytest.approx(1.0)
    assert result.tracks[-1].end.x == pytest.approx(0.0)
    assert result.tracks[-1].end.y == pytest.approx(2.0)
    assert not any(
        ev.kind == "gerber_arc_tessellation"
        for ev in result.tracks[-1].provenance.evidence
    )


def test_g75_arc_on_edge_cuts_becomes_outline_segments(tmp_path):
    p = tmp_path / "rounded_edge.gbr"
    p.write_text(
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%ADD10C,0.100*%\n"
        "D10*\n"
        "G75*\n"
        "X010000Y000000D02*\n"
        "G03X000000Y010000I-010000J000000D01*\n"
        "M02*\n"
    )

    result = GerberRS274XParser("Edge.Cuts").parse(p)

    assert not result.tracks
    assert len(result.outline) > 1
    assert result.outline[0].start.x == pytest.approx(1.0)
    assert result.outline[0].start.y == pytest.approx(0.0)
    assert result.outline[-1].end.x == pytest.approx(0.0)
    assert result.outline[-1].end.y == pytest.approx(1.0)
    assert all(
        any(ev.kind == "gerber_arc_tessellation" for ev in seg.provenance.evidence)
        for seg in result.outline
    )


def test_g74_ccw_quarter_arc_resolves_unsigned_center(tmp_path):
    p = tmp_path / "g74_ccw.gbr"
    p.write_text(
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "G74*\n"
        "X110000Y060000D02*\n"
        "G03*\n"
        "X070000Y100000I040000J000000D01*\n"
        "M02*\n"
    )

    result = GerberRS274XParser("F.Cu").parse(p)

    assert len(result.tracks) > 1
    assert result.tracks[0].start.x == pytest.approx(11.0)
    assert result.tracks[0].start.y == pytest.approx(6.0)
    assert result.tracks[-1].end.x == pytest.approx(7.0)
    assert result.tracks[-1].end.y == pytest.approx(10.0)
    assert all(
        any(
            ev.kind == "gerber_arc_tessellation"
            and "quadrant_mode=single" in ev.detail
            for ev in track.provenance.evidence
        )
        for track in result.tracks
    )


def test_g74_four_quadrants_follow_unsigned_center_semantics(tmp_path):
    p = tmp_path / "g74_four_quadrants.gbr"
    p.write_text(
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "G74*\n"
        "X110000Y060000D02*\n"
        "G03*\n"
        "X070000Y100000I040000J000000D01*\n"
        "X030000Y060000I000000J040000D01*\n"
        "X070000Y020000I040000J000000D01*\n"
        "X110000Y060000I000000J040000D01*\n"
        "M02*\n"
    )

    result = GerberRS274XParser("F.Cu").parse(p)

    assert len(result.tracks) > 4
    assert result.tracks[0].start.x == pytest.approx(11.0)
    assert result.tracks[0].start.y == pytest.approx(6.0)
    assert result.tracks[-1].end.x == pytest.approx(11.0)
    assert result.tracks[-1].end.y == pytest.approx(6.0)
    assert all(
        any(
            ev.kind == "gerber_arc_tessellation"
            and "quadrant_mode=single" in ev.detail
            for ev in track.provenance.evidence
        )
        for track in result.tracks
    )


def test_g74_zero_length_arc_emits_no_geometry(tmp_path):
    p = tmp_path / "g74_zero_length.gbr"
    p.write_text(
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "G74*\n"
        "X010000Y010000D02*\n"
        "G03*\n"
        "X010000Y010000I010000J000000D01*\n"
        "M02*\n"
    )

    result = GerberRS274XParser("F.Cu").parse(p)

    assert result.tracks == []
    assert result.diagnostics == []


def test_g74_rejects_signed_center_distances(tmp_path):
    p = tmp_path / "g74_signed.gbr"
    p.write_text(
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "G74*\n"
        "X110000Y060000D02*\n"
        "G03*\n"
        "X070000Y100000I-040000J000000D01*\n"
        "M02*\n"
    )

    with pytest.raises(ParseError):
        GerberRS274XParser("F.Cu", strict=True).parse(p)


def test_g74_rejects_arc_over_90_degrees(tmp_path):
    p = tmp_path / "g74_over_90.gbr"
    p.write_text(
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "G74*\n"
        "X010000Y000000D02*\n"
        "G03*\n"
        "X-010000Y000000I010000J000000D01*\n"
        "M02*\n"
    )

    with pytest.raises(ParseError):
        GerberRS274XParser("F.Cu", strict=True).parse(p)


def test_g75_arc_rejects_inconsistent_center_geometry(tmp_path):
    p = tmp_path / "bad_arc.gbr"
    p.write_text(
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "G75*\n"
        "X010000Y000000D02*\n"
        "G03X000000Y020000I-010000J000000D01*\n"
        "M02*\n"
    )

    with pytest.raises(ParseError):
        GerberRS274XParser("F.Cu", strict=True).parse(p)


def test_step_repeat_composes_with_g75_arc_tessellation(tmp_path):
    p = tmp_path / "panel_arc.gbr"
    p.write_text(
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%ADD10C,0.200*%\n"
        "D10*\n"
        "G75*\n"
        "X010000Y000000D02*\n"
        "%SRX2Y1I10.0J0.0*%\n"
        "G03X000000Y010000I-010000J000000D01*\n"
        "%SR*%\n"
        "M02*\n"
    )

    result = GerberRS274XParser("F.Cu").parse(p)

    assert len(result.tracks) >= 4
    assert len(result.tracks) % 2 == 0
    assert len({track.id for track in result.tracks}) == len(result.tracks)

    first_half = result.tracks[: len(result.tracks) // 2]
    second_half = result.tracks[len(result.tracks) // 2 :]
    assert first_half[0].start.x == pytest.approx(1.0)
    assert second_half[0].start.x == pytest.approx(11.0)
    assert all(
        {ev.kind for ev in track.provenance.evidence}
        >= {"gerber_step_repeat", "gerber_arc_tessellation"}
        for track in result.tracks
    )
