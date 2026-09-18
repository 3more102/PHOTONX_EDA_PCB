from photonx_eda_pcb.event_log import EventLog,query_events,validate_event
def test_event_log_query():
    l=EventLog();e=l.append("parse","parsed top layer","parser","top.gbr")
    l.append("export","wrote json","exporter")
    assert query_events(l,kind="parse")==[e]
    assert validate_event(e)==[]
