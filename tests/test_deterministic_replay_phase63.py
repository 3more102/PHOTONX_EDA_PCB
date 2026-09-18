from photonx_eda_pcb.event_log import EventLog
from photonx_eda_pcb.deterministic_replay import deterministic_replay
def test_replay_handles_iterator_and_is_deterministic():
    log=EventLog();log.append("inc","one",data={"n":1});log.append("inc","two",data={"n":2})
    handlers={"inc":lambda state,e:state.__setitem__("sum",state.get("sum",0)+e.data["n"])}
    r=deterministic_replay(iter(log.all()),handlers)
    assert r.passed and r.event_count==2
