GROUND_HINTS=("GND","GROUND","VSS","0V")
def infer_ground_nets(labels):
    out=[]
    for net_id,label in labels.items():
        s=str(label).upper().replace(" ","")
        if any(s==h or s.endswith("_"+h) for h in GROUND_HINTS):out.append(str(net_id))
    return sorted(out)
