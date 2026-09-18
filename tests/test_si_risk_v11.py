from photonx_eda_pcb.signal_integrity_risk import analyze_si_risk,validate_si_risk
def test_si_risk_combines_factors():
    x=analyze_si_risk("CLK",return_path_risk=.8,via_risk=.5,skew_risk=.2,impedance_risk=.7,length_risk=.1,confidence=.8)
    assert 0<x.score<1 and x.level in {"medium","high"}
    assert validate_si_risk(x)==[]
