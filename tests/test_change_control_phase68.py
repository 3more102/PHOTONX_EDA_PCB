from photonx_eda_pcb.eco_tracking.model import EcoSet,EcoChange
from photonx_eda_pcb.snapshot_store import SnapshotStore
from photonx_eda_pcb.event_log import EventLog
from photonx_eda_pcb.change_control import evaluate_change_control
def test_change_control_pass():
    eco=EcoSet("x",[EcoChange("E1","net","N1","rename","",True)])
    s=SnapshotStore();s.create("{}","base")
    log=EventLog();log.append("eco","approved")
    d=evaluate_change_control(eco,s,log,require_changes=True)
    assert d.passed and d.change_count==1
