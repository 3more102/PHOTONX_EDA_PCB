def debug_coverage(candidate):
    required={"SWD":2,"JTAG":4}.get(candidate.protocol,max(1,len(candidate.nets)))
    return round(min(1.0,len(candidate.nets)/required),6)
