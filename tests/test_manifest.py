from pathlib import Path

from photonx_eda_pcb.parsers.manifest import discover_manufacturing_files


FIX = Path(__file__).parent / "fixtures" / "led"


def test_manifest_classifies_inputs():
    files = discover_manufacturing_files(FIX)
    assert [f.kind for f in files].count("drill") == 1
    assert [f.kind for f in files].count("gerber") == 2
    assert any(f.layer == "Edge.Cuts" for f in files)


def test_manifest_prefers_detected_gerber_over_drill_filename(tmp_path: Path):
    p = tmp_path / "drill_map.gbr"
    p.write_text(
        "%FSLAX24Y24*%\n"
        "%MOMM*%\n"
        "%ADD10C,0.250*%\n"
        "D10*\n"
        "X010000Y010000D03*\n"
        "M02*\n",
        encoding="utf-8",
    )

    files = discover_manufacturing_files(tmp_path)

    assert len(files) == 1
    assert files[0].path == p
    assert files[0].kind == "gerber"
    assert "gerber_commands" in files[0].detection_reasons


def test_manifest_does_not_promote_known_non_manufacturing_drill_name(tmp_path: Path):
    p = tmp_path / "drill_metadata.json"
    p.write_text('{"tool": "T01"}\n', encoding="utf-8")

    assert discover_manufacturing_files(tmp_path) == []


def test_manifest_prefers_detected_excellon_over_gerber_extension(tmp_path: Path):
    p = tmp_path / "mislabelled.gbr"
    p.write_text(
        "M48\n"
        "METRIC,TZ\n"
        "T01C0.800\n"
        "%\n"
        "T01\n"
        "X1.000Y2.000\n"
        "M30\n",
        encoding="utf-8",
    )

    files = discover_manufacturing_files(tmp_path)

    assert len(files) == 1
    assert files[0].path == p
    assert files[0].kind == "drill"
    assert "excellon_header" in files[0].detection_reasons
