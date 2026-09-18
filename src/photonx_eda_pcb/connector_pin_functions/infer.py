from .model import PinFunctionCandidate
from .labels import label_function
from .protocols import protocol_function
def infer_connector_pin_functions(connector_id,pin_net_map,*,net_labels=None,signal_roles=None,protocols=(),power_nets=(),ground_nets=()):
    net_labels=net_labels or {};signal_roles=signal_roles or {};power=set(map(str,power_nets));ground=set(map(str,ground_nets));out=[]
    for pin,net in sorted(pin_net_map.items(),key=lambda x:str(x[0])):
        net=str(net);cands=[]
        if net in ground:cands.append(("ground",.99,("ground_domain",)))
        if net in power:cands.append(("power",.97,("power_domain",)))
        lf=label_function(net_labels.get(net,""))
        if lf:cands.append((lf,.92,("net_label",)))
        role_value=signal_roles.get(net)
        roles=getattr(role_value,"roles",role_value or ())
        for role in roles:
            r=str(role)
            if r=="clock":cands.append(("clock",.75,("signal_role",)))
            elif r=="reset":cands.append(("reset",.8,("signal_role",)))
            elif r=="power":cands.append(("power",.85,("signal_role",)))
            elif r=="ground":cands.append(("ground",.9,("signal_role",)))
            elif r.startswith("bus:"):cands.append(("bus_signal",.65,("bus_role",)))
        for p in protocols:
            if net not in p.net_ids:continue
            fn=protocol_function(p.protocol,net_labels.get(net,""))
            if fn:cands.append((fn,min(.9,float(p.confidence)+.1),("protocol_detection","net_label")))
            else:cands.append((str(p.protocol).lower()+"_signal",min(.75,float(p.confidence)),("protocol_detection",)))
        if not cands:cands=[("unknown",.0,("unresolved",))]
        for fn,conf,ev in cands:out.append(PinFunctionCandidate(str(connector_id),str(pin),net,fn,round(min(conf,1),6),ev))
    return out
