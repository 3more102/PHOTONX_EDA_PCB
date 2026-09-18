def priority_nets(labels):
    out=[]
    for net_id,label in labels.items():
        s=str(label).upper()
        if any(x in s for x in ("GND","VCC","VDD","RESET","CLK","SCL","SDA","TX","RX")):out.append(str(net_id))
    return sorted(out)
