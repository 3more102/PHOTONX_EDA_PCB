def build_external_interface_map(pin_functions,ports=(),protection_paths=()):
    from .model import ExternalInterfaceMap
    connectors={}
    for p in pin_functions:
        connectors.setdefault(p.connector_id,{"pins":[]})
        connectors[p.connector_id]["pins"].append({"pin":p.pin,"net_id":p.net_id,"function":p.function,"confidence":p.confidence,"conflicts":list(p.conflicts)})
    unresolved=[]
    scores=[]
    for cid,data in connectors.items():
        data["pins"].sort(key=lambda x:x["pin"])
        for p in data["pins"]:
            if p["function"] is None:unresolved.append(f"{cid}:{p['pin']}")
            else:scores.append(p["confidence"])
    for p in ports:scores.append(p.confidence)
    for p in protection_paths:scores.append(p.confidence)
    conf=round(sum(scores)/len(scores),6) if scores else 0.0
    return ExternalInterfaceMap(connectors,list(ports),list(protection_paths),conf,sorted(unresolved))
