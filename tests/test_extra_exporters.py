from photonx_eda_pcb.models import *
from photonx_eda_pcb.exporters.csv_export import export_csv_tables
from photonx_eda_pcb.exporters.graphml import export_graphml
from photonx_eda_pcb.exporters.svg import export_svg
def sample():
 b=BoardModel(tracks=[Track("T0",Point(0,0),Point(2,0),.2,"F.Cu")],pads=[PadCandidate("P0",Point(0,0),1,1,"C","F.Cu")],nets=[NetGroup("N0",["T0","P0"],.8)]); return b
def test_exporters(tmp_path):
 b=sample(); paths=export_csv_tables(b,tmp_path/"csv"); assert all(p.exists() for p in paths); assert "graphml" in export_graphml(b,tmp_path/"g.graphml").read_text(); assert "<svg" in export_svg(b,tmp_path/"b.svg").read_text()
