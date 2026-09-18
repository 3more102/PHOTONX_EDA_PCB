from photonx_eda_pcb.signal_integrity_risk import analyze_si_risk
from photonx_eda_pcb.signal_integrity_risk.ranking import rank_si_risks
def test_si_risk_ranking():
    a=analyze_si_risk("A",return_path_risk=.1);b=analyze_si_risk("B",return_path_risk=.9)
    assert rank_si_risks([a,b])[0].net_id=="B"
