from photonx_eda_pcb.clock_inference.model import ClockCandidate
from photonx_eda_pcb.reset_inference.model import ResetCandidate
from photonx_eda_pcb.thermal_risk.model import ThermalRisk
from photonx_eda_pcb.fabrication_yield.model import YieldRisk
from photonx_eda_pcb.pinmap_reconciliation.model import PinMapReport,PinMapIssue
from photonx_eda_pcb.engineering_evidence_bridge import clock_records,reset_records,thermal_records,yield_records,pinmap_records,engineering_review_items
from photonx_eda_pcb.engineering_evidence_bridge.validation import validate_bridge_records
def test_bridge_records_and_review():
    records=[]
    records+=clock_records([ClockCandidate("clk",.9,("label:CLK",),4)])
    records+=reset_records([ResetCandidate("rst",True,.8,4,("active_low_label",))])
    thermal=[ThermalRisk("U1",.7,.8,("power_estimate",),())]
    records+=thermal_records(thermal)
    yr=YieldRisk(.5,"medium",("clearance_below_rule",));records+=yield_records(yr)
    pm=PinMapReport("U2",[PinMapIssue("PIN_NAME_MISMATCH","3","OUT","SIG")],2,3);records+=pinmap_records(pm)
    assert validate_bridge_records(records)==[]
    q=engineering_review_items(thermal=thermal,yield_risk=yr,pinmap_reports=[pm])
    assert [x.kind for x in q]==["pinmap_conflict","thermal_risk","fabrication_yield"]
