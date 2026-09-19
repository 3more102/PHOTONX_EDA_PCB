from pathlib import Path

import pytest

from photonx_eda_pcb.errors import UnsupportedFeatureError
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser
from photonx_eda_pcb.pipeline import reconstruct
from photonx_eda_pcb.preflight import preflight
from photonx_eda_pcb.zones.analysis import zone_area


BASE = """%FSLAX24Y24*%
%MOMM*%
%ADD10C,0.200*%
D10*
"""


def _write(tmp_path: Path, body: str, name: str = "top.gtl") -> Path:
    path = tmp_path / name
    path.write_text(BASE + body + "M02*\n", encoding="utf-8")
    return path


def _square_region() -> str:
    return (
        "G36*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "X010000Y010000D01*\n"
        "X000000Y010000D01*\n"
        "X000000Y000000D01*\n"
        "G37*\n"
    )


def test_single_linear_closed_region_reconstructs_as_zone(tmp_path: Path):
    path = _write(tmp_path, _square_region())

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert result.tracks == []
    assert result.pads == []
    assert len(result.zones) == 1
    zone = result.zones[0]
    assert zone.layer == "F.Cu"
    assert zone.net_id is None
    assert zone.clearance_mm is None
    assert zone.min_thickness_mm is None
    assert len(zone.islands) == 1
    assert zone.islands[0].polygon == (
        (0.0, 0.0),
        (1.0, 0.0),
        (1.0, 1.0),
        (0.0, 1.0),
    )
    assert zone_area(zone) == pytest.approx(1.0)
    assert any(
        evidence.kind == "gerber_region"
        and "subset=linear_single_contour" in evidence.detail
        for evidence in zone.provenance.evidence
    )


def test_region_contour_does_not_leak_as_tracks(tmp_path: Path):
    path = _write(tmp_path, _square_region())

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.tracks == []
    assert result.pads == []
    assert len(result.zones) == 1


def test_region_can_appear_between_other_graphical_objects(tmp_path: Path):
    path = _write(
        tmp_path,
        "X000000Y020000D02*\n"
        "X010000Y020000D01*\n"
        + _square_region()
        + "X020000Y020000D02*\n"
        "X030000Y020000D01*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.tracks) == 2
    assert len(result.zones) == 1


def test_region_preflight_is_ready_for_strict_reconstruction(tmp_path: Path):
    path = _write(tmp_path, _square_region())

    report = preflight(path)

    assert report.discovered_files == 1
    assert report.ready_for_strict_reconstruction
    assert not report.strict_blockers


def test_pipeline_carries_region_into_board_model(tmp_path: Path):
    _write(tmp_path, _square_region(), name="board.gtl")

    reconstructed = reconstruct(tmp_path)

    assert len(reconstructed.board.zones) == 1
    zone = reconstructed.board.zones[0]
    assert reconstructed.board.object_index()[zone.id] is zone
    assert any(
        issue.code == "ZONE_NET_UNRESOLVED"
        for issue in reconstructed.validation.warnings
    )


def test_region_step_repeat_creates_distinct_zones_without_scaling_sr_distance(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "%SFA2B2*%\n"
        "%SRX2Y1I3.0J0*%\n"
        + _square_region()
        + "%SR*%\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.zones) == 2
    assert result.zones[0].id != result.zones[1].id
    first = result.zones[0].islands[0].polygon
    second = result.zones[1].islands[0].polygon
    assert first == ((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))
    assert second == ((3.0, 0.0), (5.0, 0.0), (5.0, 2.0), (3.0, 2.0))


def test_region_composes_with_mi_sf_of_ir(tmp_path: Path):
    path = _write(
        tmp_path,
        "%MIA1*%\n"
        "%SFA2B1*%\n"
        "%OFA3B4*%\n"
        "%IR90*%\n"
        + _square_region(),
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    polygon = result.zones[0].islands[0].polygon
    # Source (0,0),(1,0),(1,1),(0,1)
    # MI-X -> (0,0),(-1,0),(-1,1),(0,1)
    # SF -> (0,0),(-2,0),(-2,1),(0,1)
    # OF -> (3,4),(1,4),(1,5),(3,5)
    # IR90 -> (-4,3),(-4,1),(-5,1),(-5,3)
    assert polygon == ((-4.0, 3.0), (-4.0, 1.0), (-5.0, 1.0), (-5.0, 3.0))


def test_region_direction_is_not_significant(tmp_path: Path):
    path = _write(
        tmp_path,
        "G36*\n"
        "X000000Y000000D02*\n"
        "X000000Y010000D01*\n"
        "X010000Y010000D01*\n"
        "X010000Y000000D01*\n"
        "X000000Y000000D01*\n"
        "G37*\n",
    )

    result = GerberRS274XParser("F.Cu", strict=True).parse(path)

    assert len(result.zones) == 1
    assert zone_area(result.zones[0]) == pytest.approx(1.0)


def test_open_region_contour_fails_closed(tmp_path: Path):
    path = _write(
        tmp_path,
        "G36*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "X010000Y010000D01*\n"
        "X000000Y010000D01*\n"
        "G37*\n",
    )

    with pytest.raises(
        UnsupportedFeatureError,
        match="does not implicitly close",
    ):
        GerberRS274XParser("F.Cu", strict=True).parse(path)

    permissive = GerberRS274XParser("F.Cu", strict=False).parse(path)
    assert permissive.zones == []
    assert any(
        d.code == "INVALID_GERBER_REGION_OPEN_CONTOUR"
        for d in permissive.diagnostics
    )


def test_self_intersecting_region_fails_closed(tmp_path: Path):
    path = _write(
        tmp_path,
        "G36*\n"
        "X000000Y000000D02*\n"
        "X020000Y020000D01*\n"
        "X000000Y020000D01*\n"
        "X020000Y000000D01*\n"
        "X000000Y000000D01*\n"
        "G37*\n",
    )

    with pytest.raises(
        UnsupportedFeatureError,
        match="simple non-self-intersecting polygon",
    ):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_second_d02_multicontour_region_remains_fail_closed(tmp_path: Path):
    path = _write(
        tmp_path,
        _square_region().replace(
            "G37*\n",
            "X020000Y020000D02*\n"
            "X030000Y020000D01*\n"
            "X030000Y030000D01*\n"
            "X020000Y020000D01*\n"
            "G37*\n",
        ),
    )

    with pytest.raises(
        UnsupportedFeatureError,
        match="exactly one contour",
    ):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_region_arc_remains_fail_closed(tmp_path: Path):
    path = _write(
        tmp_path,
        "G75*\n"
        "G36*\n"
        "X010000Y000000D02*\n"
        "G03X000000Y010000I-010000J000000D01*\n"
        "G37*\n",
    )

    with pytest.raises(
        UnsupportedFeatureError,
        match="does not yet support circular contour segments",
    ):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_region_flash_is_invalid(tmp_path: Path):
    path = _write(
        tmp_path,
        "G36*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D03*\n"
        "G37*\n",
    )

    with pytest.raises(
        UnsupportedFeatureError,
        match="D03 flash is not valid",
    ):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_unsupported_command_inside_region_fails_closed(tmp_path: Path):
    path = _write(
        tmp_path,
        "G36*\n"
        "X000000Y000000D02*\n"
        "%LS2*%\n"
        "G37*\n",
    )

    with pytest.raises(
        UnsupportedFeatureError,
        match="allows only D01/D02",
    ):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_unterminated_region_at_eof_fails_closed(tmp_path: Path):
    path = _write(
        tmp_path,
        "G36*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "X000000Y000000D01*\n",
    )

    with pytest.raises(
        UnsupportedFeatureError,
        match="before closing an active G36 region",
    ):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_aperture_block_fails_closed_in_strict_mode(tmp_path: Path):
    path = _write(
        tmp_path,
        "%ABD11*%\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "%AB*%\n",
    )

    with pytest.raises(
        UnsupportedFeatureError,
        match="aperture blocks are not implemented safely",
    ):
        GerberRS274XParser("F.Cu", strict=True).parse(path)


def test_aperture_block_body_does_not_leak_geometry_in_permissive_mode(
    tmp_path: Path,
):
    path = _write(
        tmp_path,
        "%ABD11*%\n"
        "X010000Y010000D03*\n"
        "X000000Y000000D02*\n"
        "X010000Y000000D01*\n"
        "%AB*%\n",
    )

    result = GerberRS274XParser("F.Cu", strict=False).parse(path)

    assert result.tracks == []
    assert result.pads == []
    assert result.outline == []
    assert result.zones == []


def test_preflight_still_blocks_aperture_blocks(tmp_path: Path):
    path = _write(tmp_path, "%ABD11*%\n%AB*%\n")

    report = preflight(path)

    assert report.discovered_files == 1
    assert not report.ready_for_strict_reconstruction
    assert any(
        "UNSUPPORTED_GERBER_CONSTRUCT" in blocker
        for blocker in report.strict_blockers
    )
