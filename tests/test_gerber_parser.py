from pathlib import Path
import pytest
from photonx_eda_pcb.parsers.gerber_rs274x import GerberRS274XParser
from photonx_eda_pcb.errors import UnsupportedFeatureError
FIX = Path(__file__).parent / "fixtures" / "led"

def test_copper_parser_extracts_evidence_objects():
    result=GerberRS274XParser("F.Cu").parse(FIX/"copper.gbr"); assert len(result.pads)==6; assert len(result.tracks)==4; assert all(p.provenance.sources for p in result.pads); assert all(t.provenance.sources for t in result.tracks)

def test_outline_parser_keeps_outline_separate():
    result=GerberRS274XParser("Edge.Cuts").parse(FIX/"outline.gbr"); assert len(result.outline)==4; assert not result.tracks

def test_unsupported_arc_is_not_silently_ignored(tmp_path):
    p=tmp_path/"arc.gbr"; p.write_text("%FSLAX24Y24*%\n%MOMM*%\n%ADD10C,0.2*%\nD10*\nG02X010000Y010000I000500J000000D01*\nM02*\n")
    with pytest.raises(UnsupportedFeatureError): GerberRS274XParser("F.Cu",strict=True).parse(p)
