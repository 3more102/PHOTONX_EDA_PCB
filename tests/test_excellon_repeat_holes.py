import pytest

from photonx_eda_pcb.errors import ParseError, UnsupportedFeatureError
from photonx_eda_pcb.parsers.excellon import ExcellonParser


def _write(tmp_path, body: str):
    path = tmp_path / "repeat.drl"
    path.write_text(body, encoding="utf-8")
    return path


def _coords(result):
    return [(drill.center.x, drill.center.y) for drill in result.drills]


def test_repeat_hole_expands_incremental_steps_from_previous_hit(tmp_path):
    path = _write(
        tmp_path,
        """M48
METRIC
T01C0.800
%
T01
X1.000Y2.000
R3X0.500Y-0.250
M30
""",
    )

    result = ExcellonParser(strict=True).parse(path)

    assert [x for x, _ in _coords(result)] == pytest.approx([1.0, 1.5, 2.0, 2.5])
    assert [y for _, y in _coords(result)] == pytest.approx([2.0, 1.75, 1.5, 1.25])
    assert [drill.tool for drill in result.drills] == ["T01"] * 4
    assert [drill.diameter for drill in result.drills] == pytest.approx([0.8] * 4)
    assert len({drill.id for drill in result.drills}) == 4

    repeated = result.drills[1:]
    assert all(
        any(event.kind == "excellon_repeat_hole" for event in drill.provenance.evidence)
        for drill in repeated
    )
    assert {
        drill.provenance.sources[0].raw
        for drill in repeated
    } == {"R3X0.500Y-0.250"}


def test_repeat_hole_does_not_change_global_incremental_mode(tmp_path):
    path = _write(
        tmp_path,
        """M48
METRIC
T01C0.800
%
T01
X1.000Y2.000
G91
R2X0.500
X0.250Y0.000
M30
""",
    )

    result = ExcellonParser(strict=True).parse(path)

    assert [x for x, _ in _coords(result)] == pytest.approx([1.0, 1.5, 2.0, 2.25])
    assert [y for _, y in _coords(result)] == pytest.approx([2.0, 2.0, 2.0, 2.0])


def test_repeat_hole_without_xy_repeats_same_location(tmp_path):
    path = _write(
        tmp_path,
        """M48
METRIC
T01C0.800
%
T01
X1.000Y2.000
R2
M30
""",
    )

    result = ExcellonParser(strict=True).parse(path)

    assert _coords(result) == [(1.0, 2.0), (1.0, 2.0), (1.0, 2.0)]
    assert len({drill.id for drill in result.drills}) == 3


def test_repeat_hole_requires_preceding_drill_anchor(tmp_path):
    path = _write(
        tmp_path,
        """M48
METRIC
T01C0.800
%
T01
R2X0.500
M30
""",
    )

    with pytest.raises(ParseError, match="requires a preceding drill hit"):
        ExcellonParser(strict=True).parse(path)

    result = ExcellonParser(strict=False).parse(path)
    assert result.drills == []
    assert [diagnostic.code for diagnostic in result.diagnostics] == [
        "EXCELLON_REPEAT_NO_ANCHOR"
    ]


def test_route_position_invalidates_repeat_hole_anchor(tmp_path):
    path = _write(
        tmp_path,
        """M48
METRIC
T01C0.800
%
T01
X1.000Y2.000
G00X4.000Y5.000
R2X0.500
M30
""",
    )

    with pytest.raises(ParseError, match="requires a preceding drill hit"):
        ExcellonParser(strict=True).parse(path)


def test_repeat_hole_expansion_is_bounded(tmp_path):
    path = _write(
        tmp_path,
        """M48
METRIC
T01C0.800
%
T01
X1.000Y2.000
R10001X0.001
M30
""",
    )

    with pytest.raises(UnsupportedFeatureError, match="exceeds safety limit"):
        ExcellonParser(strict=True).parse(path)

    result = ExcellonParser(strict=False).parse(path)
    assert result.drills == []
    assert [diagnostic.code for diagnostic in result.diagnostics] == [
        "EXCELLON_REPEAT_LIMIT"
    ]


def test_malformed_repeat_hole_syntax_fails_closed(tmp_path):
    path = _write(
        tmp_path,
        """M48
METRIC
T01C0.800
%
T01
X1.000Y2.000
R2X0.500Q1
M30
""",
    )

    with pytest.raises(UnsupportedFeatureError, match="repeat-hole syntax"):
        ExcellonParser(strict=True).parse(path)

    result = ExcellonParser(strict=False).parse(path)
    assert result.drills == []
    assert [diagnostic.code for diagnostic in result.diagnostics] == [
        "UNSUPPORTED_EXCELLON_REPEAT_SYNTAX"
    ]
