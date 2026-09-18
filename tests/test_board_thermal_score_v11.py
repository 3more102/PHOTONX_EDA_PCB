from photonx_eda_pcb.thermal_risk import ThermalObservation,analyze_thermal_risk
from photonx_eda_pcb.thermal_risk.board import board_thermal_score
def test_board_thermal_score():
    items=[analyze_thermal_risk(ThermalObservation("A",2,20,2)),analyze_thermal_risk(ThermalObservation("B",1,50,4))]
    assert 0<board_thermal_score(items)<1
