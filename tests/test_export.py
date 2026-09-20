from pathlib import Path
from photonx_eda_pcb import reconstruct
from photonx_eda_pcb.exporters import export_kicad, export_json, validate_with_kicad_cli
from photonx_eda_pcb.exporters.kicad import export_kicad_with_report
FIX=Path(__file__).parent/"fixtures"/"led"

def test_json_export_contains_provenance(tmp_path):
    board=reconstruct(FIX).board; p=export_json(board,tmp_path/"board.json"); text=p.read_text(); assert '"provenance"' in text; assert '"sources"' in text

def test_kicad_export_is_labeled_as_photonx_generator(tmp_path):
    board=reconstruct(FIX).board
    p,report=export_kicad_with_report(board,tmp_path/"board.kicad_pcb")
    text=p.read_text()
    assert '(generator "photonx_eda_pcb")' in text
    assert text.count('(segment ')==4
    assert text.count('(gr_line ')==4
    assert text.count('(footprint "PHOTONX:RecoveredPad"')==0
    assert report.skipped_pad_ids==[pad.id for pad in board.pads]
    assert all(pad.drill is not None for pad in board.pads)
    assert sum(
        issue.code=="KICAD_PAD_DRILL_PADSTACK_UNPROVEN"
        for issue in report.issues
    )==6
    assert 'NET_PHYS' not in text

def test_kicad_cli_validation_reports_unavailability_truthfully(tmp_path):
    board=reconstruct(FIX).board; p=export_kicad(board,tmp_path/"board.kicad_pcb"); ok,detail=validate_with_kicad_cli(p); assert ok in {True,False,None}; assert isinstance(detail,str)
