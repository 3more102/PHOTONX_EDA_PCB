from photonx_eda_pcb.thermal_risk import ThermalObservation,analyze_thermal_risk,validate_thermal_risk
from photonx_eda_pcb.thermal_risk.classify import risk_level
def test_thermal_risk():
    r=analyze_thermal_risk(ThermalObservation("U1",power_w=4,copper_area_mm2=5,thermal_vias=0,ambient_c=50))
    assert r.risk>.4 and r.confidence>.5
    assert risk_level(r.risk) in {"medium","high"}
    assert validate_thermal_risk(r)==[]
