from photonx_eda_pcb.event_log import EventLog
from photonx_eda_pcb.event_log.replay import replay
def test_event_replay():
    l=EventLog();l.append("inc","one",data={"n":2});l.append("inc","two",data={"n":3})
    state=replay(l.all(),{"inc":lambda s,e:s.__setitem__("x",s.get("x",0)+e.data["n"])},{})
    assert state["x"]==5
