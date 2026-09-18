from pathlib import Path
import zipfile

import pytest

from photonx_eda_pcb.input_package import prepare_input
from photonx_eda_pcb.parsers.layer_map import infer_layer
from photonx_eda_pcb.parsers.manifest import discover_manufacturing_files
from photonx_eda_pcb.pipeline import reconstruct
from photonx_eda_pcb.preflight import preflight


GERBER_LINEAR = """%FSLAX24Y24*%
%MOMM*%
%ADD10C,0.200*%
D10*
X000000Y000000D02*
X010000Y000000D01*
M02*
"""


def test_content_detection_finds_extensionless_gerber(tmp_path: Path):
    p = tmp_path / "CAM_LAYER_01"
    p.write_text(GERBER_LINEAR, encoding="utf-8")

    files = discover_manufacturing_files(tmp_path)

    assert len(files) == 1
    assert files[0].kind == "gerber"
    assert files[0].format_confidence >= 0.8


def test_discovery_is_recursive(tmp_path: Path):
    nested = tmp_path / "fab" / "layers"
    nested.mkdir(parents=True)
    (nested / "top.gtl").write_text(GERBER_LINEAR, encoding="utf-8")

    files = discover_manufacturing_files(tmp_path)

    assert len(files) == 1
    assert files[0].layer == "F.Cu"


def test_x2_file_function_is_used_before_filename():
    text = "%TF.FileFunction,Copper,L1,Top*%\n" + GERBER_LINEAR
    assert infer_layer("unknown.dat", text) == "F.Cu"

    text = "%TF.FileFunction,Soldermask,Bot*%\n" + GERBER_LINEAR
    assert infer_layer("unknown.dat", text) == "B.Mask"


def test_zip_package_can_be_reconstructed(tmp_path: Path):
    archive = tmp_path / "board.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("nested/top.gtl", GERBER_LINEAR)

    result = reconstruct(archive)

    assert result.board.metadata["input_kind"] == "zip"
    assert result.board.metadata["manufacturing_file_count"] == 1
    assert len(result.board.tracks) == 1


def test_preflight_reports_strict_blocker_without_silent_drop(tmp_path: Path):
    p = tmp_path / "top.gtl"
    p.write_text(
        "%FSLAX24Y24*%\n%MOMM*%\nG36*\nM02*\n",
        encoding="utf-8",
    )

    report = preflight(tmp_path)

    assert report.discovered_files == 1
    assert not report.ready_for_strict_reconstruction
    assert any(
        "UNSUPPORTED_GERBER_CONSTRUCT" in blocker
        for blocker in report.strict_blockers
    )


def test_zip_path_traversal_is_rejected(tmp_path: Path):
    archive = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("../escape.gtl", GERBER_LINEAR)

    with pytest.raises(ValueError, match="unsafe archive member"):
        with prepare_input(archive):
            pass
