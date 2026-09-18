import networkx as nx
from photonx_eda_pcb.functional_blocks.model import FunctionalBlock
from photonx_eda_pcb.page_partitioning import partition_blocks
from photonx_eda_pcb.schematic_autolayout import build_layout_plan,apply_layout
from photonx_eda_pcb.schematic_editor import *
from photonx_eda_pcb.schematic_editor.pages import ensure_page
from photonx_eda_pcb.kicad_schematic_export import export_document_from_editor,write_export_document
from photonx_eda_pcb.kicad_schematic_roundtrip import read_schematic_text
def test_blocks_to_layout_to_kicad():
    blocks=[FunctionalBlock("b",("U1","R1"),("N1",),"compute",.8)]
    part=partition_blocks(blocks,10)[0]
    g=nx.Graph();g.add_edges_from([("C:U1","N:N1"),("N:N1","C:R1")])
    layout=apply_layout(g,build_layout_plan(part))
    d=EditorDocument();ensure_page(d,part.id,part.title)
    for cid,(x,y) in layout.positions.items():
        add_object(d,EditorSymbol("s:"+cid,cid,"PHOTONX:Unknown",cid,"?",x,y,page_id=part.id,confidence=.5))
    for i,r in enumerate(layout.routes):add_object(d,EditorWire("w:"+str(i),r.net_id,r.points,page_id=part.id))
    data=read_schematic_text(write_export_document(export_document_from_editor(d,"Demo")))
    assert len(data["symbols"])==2 and len(data["wires"])==1
