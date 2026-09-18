from photonx_eda_pcb.return_path import analyze_return_path
from photonx_eda_pcb.return_path.risk import return_path_risk
from photonx_eda_pcb.via_transition import analyze_transition
from photonx_eda_pcb.via_transition.quality import transition_quality
from photonx_eda_pcb.signal_integrity_risk import analyze_si_risk
from photonx_eda_pcb.differential_pair_quality import analyze_pair_quality
from photonx_eda_pcb.current_capacity import estimate_current_capacity
from photonx_eda_pcb.quality_dashboard import build_dashboard
def test_phase11_quality_flow():
    rp=analyze_return_path("USB_P",plane="GND",continuity_samples=[1,1,1],signal_vias=1,return_vias=1)
    via=analyze_transition("V1","USB_P","F.Cu","B.Cu",.3,.7,1,0)
    pair=analyze_pair_quality("USB_P","USB_N",skew_mm=.05,spacing_variation_mm=.02,confidence=.8)
    si=analyze_si_risk("USB_P",return_path_risk=return_path_risk(rp),via_risk=1-transition_quality(via),skew_risk=1-pair.score,confidence=.8)
    cap=estimate_current_capacity("VCC",.5)
    d=build_dashboard({"si":{"score":1-si.score},"diff_pair":pair.score,"current_capacity":{"score":min(1,cap.estimated_current_a)}})
    assert 0<=d.overall_score<=1
