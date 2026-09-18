def infer_role(label):
    s=str(label or "").upper()
    if any(x in s for x in ("GND","VSS","GROUND")):return "ground",.95
    if any(x in s for x in ("VCC","VDD","+5V","+3V3","VBUS","VBAT")):return "power",.9
    if any(x in s for x in ("TX","MOSI","SDA","D+","CANH")):return "signal_out_or_bidir",.65
    if any(x in s for x in ("RX","MISO","SCL","D-","CANL")):return "signal_in_or_bidir",.65
    return "signal",.4
