def quote(value):
    s=str(value).replace("\\","\\\\").replace('"','\\"').replace("\n","\\n")
    return '"'+s+'"'
def number(value):
    x=round(float(value),4)
    return str(int(x)) if x.is_integer() else ("%.4f"%x).rstrip("0").rstrip(".")
