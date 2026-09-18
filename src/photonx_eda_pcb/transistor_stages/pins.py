GATE_NAMES={"G","GATE","B","BASE"};SOURCE_NAMES={"S","SOURCE","E","EMITTER"};DRAIN_NAMES={"D","DRAIN","C","COLLECTOR"}
def transistor_pin_roles(pin_names):
    out={}
    for pin,name in pin_names.items():
        n=str(name).upper()
        if n in GATE_NAMES:out["control"]=str(pin)
        elif n in SOURCE_NAMES:out["source"]=str(pin)
        elif n in DRAIN_NAMES:out["load"]=str(pin)
    return out
