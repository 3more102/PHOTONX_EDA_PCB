from pathlib import Path

from photonx_eda_pcb.parsers.layer_map import (
    x2_file_function_declarations,
    x2_file_function_fields,
)
from photonx_eda_pcb.parsers.manifest import discover_manufacturing_files
from photonx_eda_pcb.pipeline import reconstruct


GERBER_BODY = """%FSLAX24Y24*%
%MOMM*%
%ADD10C,1.000*%
D10*
X010000Y010000D03*
M02*
"""


def _with_functions(*values: str) -> str:
    attrs = "".join(f"%TF.FileFunction,{value}*%\n" for value in values)
    return attrs + GERBER_BODY


def test_file_function_is_unique_immutable_attribute():
    text = _with_functions("Copper,L1,Top", "Copper,L2,Bot")

    assert x2_file_function_declarations(text) == (
        ("Copper", "L1", "Top"),
        ("Copper", "L2", "Bot"),
    )
    assert x2_file_function_fields(text) is None


def test_manifest_fails_closed_on_redefined_file_function(tmp_path: Path):
    path = tmp_path / "top.gtl"
    path.write_text(
        _with_functions("Copper,L1,Top", "Copper,L2,Bot"),
        encoding="utf-8",
    )

    files = discover_manufacturing_files(tmp_path)

    assert len(files) == 1
    assert files[0].kind == "gerber"
    assert files[0].layer is None
    assert files[0].x2_file_function == ()
    assert files[0].x2_file_function_conflict is True


def test_pipeline_skips_redefined_file_function_instead_of_guessing_filename(
    tmp_path: Path,
):
    (tmp_path / "top.gtl").write_text(
        _with_functions("Copper,L1,Top", "Copper,L2,Bot"),
        encoding="utf-8",
    )
    (tmp_path / "bottom.gbl").write_text(
        _with_functions("Copper,L2,Bot"),
        encoding="utf-8",
    )

    board = reconstruct(tmp_path).board

    assert [pad.layer for pad in board.pads] == ["B.Cu"]
    issues = [
        item for item in board.diagnostics
        if item.code == "X2_FILE_FUNCTION_REDEFINED"
    ]
    assert len(issues) == 1
    assert issues[0].path.endswith("top.gtl")
