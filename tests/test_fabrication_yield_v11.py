from photonx_eda_pcb.fabrication_yield import FabricationMetrics,estimate_yield_risk,validate_yield_risk
def test_yield_risk_drivers():
    m=FabricationMetrics(track_count=100,min_track_mm=.1,min_clearance_mm=.1,drill_count=10,min_drill_mm=.15,via_count=50,board_area_mm2=100,acute_features=3)
    r=estimate_yield_risk(m)
    assert r.score>.5 and "track_below_rule" in r.drivers
    assert validate_yield_risk(r)==[]
