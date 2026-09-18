from .model import NetNameCandidate
def heuristic_power_names(net_features):
    out=[]
    for net_id,f in net_features.items():
        if f.get("is_ground"):out.append(NetNameCandidate(str(net_id),"GND",.55,"heuristic","ground_topology"))
        elif f.get("is_power"):out.append(NetNameCandidate(str(net_id),f.get("hint","POWER"),.45,"heuristic","power_topology"))
    return out
