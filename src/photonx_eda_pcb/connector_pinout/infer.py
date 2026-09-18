from .model import PinoutCandidate,ConnectorPinout
from .roles import infer_role
def infer_pinout(component_id,pin_to_net,labels):
    pins=[]
    for pin,net in sorted(pin_to_net.items(),key=lambda x:str(x[0])):
        label=labels.get(net,"") if net is not None else ""
        role,confidence=infer_role(label)
        ev=("net_label",) if label else ("connectivity_only",)
        pins.append(PinoutCandidate(str(pin),None if net is None else str(net),role,confidence,ev))
    return ConnectorPinout(str(component_id),pins)
