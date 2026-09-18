from .model import RegulatorCandidate
from .kinds import regulator_kind
from .pins import classify_pin_name
def infer_regulators(identity_by_id,pin_net_map,pin_names=None):
    pin_names=pin_names or {};out=[]
    for cid,identity in sorted(identity_by_id.items()):
        kind=regulator_kind(identity)
        if kind is None:continue
        inputs=[];outputs=[];enable=[];feedback=[];named=0
        for pin,net in pin_net_map.get(cid,{}).items():
            role=classify_pin_name(pin_names.get(cid,{}).get(pin,""))
            if role!="unknown":named+=1
            if role=="input":inputs.append(str(net))
            elif role=="output":outputs.append(str(net))
            elif role=="enable":enable.append(str(net))
            elif role=="feedback":feedback.append(str(net))
        score=.55+(.08 if inputs else 0)+(.12 if outputs else 0)+(.05 if enable else 0)+(.05 if feedback else 0)+min(.1,.02*named)
        ev=["component_identity"]
        if named:ev.append("pin_names")
        if inputs or outputs:ev.append("rail_pins")
        out.append(RegulatorCandidate(str(cid),kind,tuple(sorted(set(inputs))),tuple(sorted(set(outputs))),tuple(sorted(set(enable))),tuple(sorted(set(feedback))),round(min(score,1),6),tuple(ev)))
    return out
