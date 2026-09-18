from .model import NetNameCandidate
from .normalize import normalize_net_name
def candidates_from_labels(labels,source="netlist"):
    return [NetNameCandidate(str(net_id),normalize_net_name(name),.95,str(source),"explicit_label") for net_id,name in labels.items() if normalize_net_name(name)]
