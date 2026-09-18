from photonx_eda_pcb.milestone_readiness import MilestoneInput,evaluate_phase70
from photonx_eda_pcb.milestone_readiness.dashboard import readiness_dashboard
def test_phase70_dashboard():
    d=readiness_dashboard(evaluate_phase70(MilestoneInput(True,True,True,True,True,True,0,0,1,1)))
    assert d.overall_score==1.0 and d.cards[0].name=="phase70"
