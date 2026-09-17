from pathlib import Path
from photonx_eda_pcb import load_project, export_kicad

ROOT=Path(__file__).parents[1]
INPUT=ROOT/'examples'/'PHOTONX_LED_TEST'/'input'

def test_parse_counts():
    b=load_project(INPUT)
    assert len(b.pads)==6
    assert len(b.tracks)==4
    assert len(b.holes)==6
    assert len(b.outline.segments)==4

def test_connectivity_reconstructs_three_nets():
    b=load_project(INPUT)
    assert len(b.nets)==3
    sizes=sorted(len(v) for v in b.nets.values())
    assert sizes==[3,3,4]

def test_component_hypotheses():
    b=load_project(INPUT)
    assert len(b.components)==3
    assert all(len(c.pad_ids)==2 for c in b.components)
    assert all(c.confidence>0.5 for c in b.components)

def test_kicad_export(tmp_path):
    b=load_project(INPUT)
    p=export_kicad(b,tmp_path/'out.kicad_pcb')
    text=p.read_text()
    assert '(kicad_pcb' in text
    assert text.count('(segment ')==4
    assert text.count('(footprint ')==6
    assert 'Edge.Cuts' in text
