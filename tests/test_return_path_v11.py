from photonx_eda_pcb.return_path import analyze_return_path,validate_return_path
from photonx_eda_pcb.return_path.risk import return_path_risk
def test_return_path_good():
    e=analyze_return_path("N1",plane="GND",continuity_samples=[1,1,1,1],signal_vias=1,return_vias=1)
    assert e.continuity_score==1.0 and e.via_penalty==0.0
    assert return_path_risk(e)==0.0
    assert validate_return_path(e)==[]
def test_return_path_split_risk():
    e=analyze_return_path("N1",plane="GND",continuity_samples=[1,0],split_crossings=2)
    assert return_path_risk(e)>0.5
