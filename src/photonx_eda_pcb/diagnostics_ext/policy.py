SEVERITY_ORDER={"info":0,"warning":1,"error":2,"fatal":3}
def at_least(severity,minimum): return SEVERITY_ORDER[severity]>=SEVERITY_ORDER[minimum]
