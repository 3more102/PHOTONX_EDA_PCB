POWER_HINTS=("VCC","VDD","+5V","+3V3","+12V","VBAT")
def infer_power_nets(labels):
    out=[]
    for net_id,label in labels.items():
        s=str(label).upper().replace(" ","")
        if any(h in s for h in POWER_HINTS):out.append(str(net_id))
    return sorted(out)
