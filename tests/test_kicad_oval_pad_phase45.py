from photonx_eda_pcb.models import BoardModel,PadCandidate,Point
from photonx_eda_pcb.exporters.kicad import export_kicad_with_report

def test_kicad_oval_pad_shape(tmp_path):
    b=BoardModel(pads=[PadCandidate("P",Point(1,2),4,2,"O","F.Cu")])
    p,r=export_kicad_with_report(b,tmp_path/"x.kicad_pcb")
    text=p.read_text()
    assert '(pad "1" smd oval' in text
    assert r.ok
