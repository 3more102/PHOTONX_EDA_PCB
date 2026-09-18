from photonx_eda_pcb.event_log.replay import replay
from .hash import stable_hash
from .model import ReplayResult
def deterministic_replay(events,handlers,initial_factory=lambda:{}):
    events=list(events)
    a=replay(events,handlers,initial_factory());b=replay(events,handlers,initial_factory())
    ha,hb=stable_hash(a),stable_hash(b)
    return ReplayResult(ha==hb,ha,hb,len(events))
