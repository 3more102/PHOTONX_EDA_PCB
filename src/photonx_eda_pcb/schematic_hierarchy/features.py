def component_features(component_id,kind,net_ids):
    return {"component_id":str(component_id),"kind":str(kind).lower(),"net_ids":tuple(sorted(map(str,net_ids)))}
def block_key(kind,net_ids):
    k=str(kind).lower()
    if any(x in k for x in ("connector","usb","ethernet")):return "io"
    if any(x in k for x in ("regulator","ldo","dc-dc","power")):return "power"
    if any(x in k for x in ("mcu","cpu","fpga","soc")):return "compute"
    labels=" ".join(map(str,net_ids)).upper()
    if any(x in labels for x in ("VCC","VDD","GND","VBAT")):return "power"
    return "logic"
