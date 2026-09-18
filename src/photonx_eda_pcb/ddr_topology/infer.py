from .model import DdrLane,DdrTopology
from .grouping import group_ddr_nets
from .components import classify_components
def infer_ddr_topology(labels,identity_by_id=None):
    groups=group_ddr_nets(labels);lanes=[];e=[];score=0.0
    for role,nets in groups.items():
        conf=.8 if len(nets)>=2 else .65
        lanes.append(DdrLane(role,nets,role,conf));score+=min(.15,.02*len(nets));e.append("label_group:"+role)
    controllers,memories=classify_components(identity_by_id or {})
    controller=controllers[0] if controllers else None
    if controller:score+=.2;e.append("controller_identity")
    if memories:score+=.25;e.append("memory_identity")
    if "data" in groups and ("strobe" in groups or "clock" in groups):score+=.25;e.append("ddr_signal_pattern")
    return DdrTopology(lanes,controller,memories,round(min(score,1.0),12),e)
