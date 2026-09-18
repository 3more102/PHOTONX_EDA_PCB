from photonx_eda_pcb.eco_tracking.model import EcoSet,EcoChange
from photonx_eda_pcb.snapshot_store import SnapshotStore
from photonx_eda_pcb.event_log import EventLog
from photonx_eda_pcb.change_control import evaluate_change_control
def test_unapproved_eco_blocks():
    eco=EcoSet("x",[EcoChange("E1","net","N","rename")]);s=SnapshotStore();s.create("{}");log=EventLog();log.append("eco","x")
    assert "CHANGE_CONTROL_UNAPPROVED_ECO" in evaluate_change_control(eco,s,log).blockers
