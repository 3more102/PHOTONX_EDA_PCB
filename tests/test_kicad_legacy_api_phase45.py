from photonx_eda_pcb.models import BoardModel
from photonx_eda_pcb.exporters.kicad import export_kicad

def test_legacy_export_kicad_still_returns_path(tmp_path):
    p=export_kicad(BoardModel(),tmp_path/"x.kicad_pcb")
    assert p.exists()
