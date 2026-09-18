import pytest
from photonx_eda_pcb.project_file_format.paths import normalize_project_path
def test_rejects_parent_escape():
    with pytest.raises(ValueError):normalize_project_path("../secret.txt")
def test_normalizes_windows_slashes():
    assert normalize_project_path("fab\\top.gbr")=="fab/top.gbr"
