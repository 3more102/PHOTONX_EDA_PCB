from photonx_eda_pcb.source_alignment.transform import AlignmentTransform
from photonx_eda_pcb.source_alignment.report import alignment_report
def test_alignment_report():
    r=alignment_report(AlignmentTransform(1,2,1,0),.01)
    assert r["dx"]==1 and r["rms_error"]==.01
