from photonx_eda_pcb.manufacturing_risk import RiskItem,aggregate_risk,validate_risk
def test_manufacturing_risk():
    r=aggregate_risk([RiskItem("assembly","A",.2),RiskItem("mechanical","B",.8)])
    assert r.score==.5 and r.level=="medium" and validate_risk(r)==[]
