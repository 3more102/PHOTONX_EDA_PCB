from .model import NetClassCandidate
from .features import net_features
from .rules import classify_features
def infer_net_classes(net_data):
    out=[]
    for item in net_data:
        f=net_features(item["net_id"],item.get("label",""),item.get("widths",()),item.get("is_diff",False),item.get("degree",0))
        name,confidence,evidence=classify_features(f)
        out.append(NetClassCandidate(f["net_id"],name,confidence,evidence))
    return sorted(out,key=lambda x:x.net_id)
