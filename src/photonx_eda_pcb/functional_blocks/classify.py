def classify_block(kinds,roles):
    k=set(kinds);r=set(roles)
    if any("connector" in x for x in k):return "interface"
    if any(x in r for x in ("power","ground")) and any("regulator" in x or "power" in x for x in k):return "power"
    if any("memory" in x or "ddr" in x for x in k):return "memory"
    if any("sensor" in x for x in k):return "sensor"
    if any("clock" in x or "oscillator" in x for x in k):return "clocking"
    if any("mcu" in x or "cpu" in x or "fpga" in x or "soc" in x for x in k):return "compute"
    return "unknown"
