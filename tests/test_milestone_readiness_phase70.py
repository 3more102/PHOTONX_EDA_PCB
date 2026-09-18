from photonx_eda_pcb.milestone_readiness import MilestoneInput,evaluate_phase70
def test_phase70_ready():
    x=MilestoneInput(True,True,True,True,True,True,0,0,1.0,1.0)
    r=evaluate_phase70(x)
    assert r.passed and r.phase==70 and r.score==1.0
