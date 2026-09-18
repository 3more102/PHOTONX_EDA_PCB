def collect_metric(boards,key):
    out=[]
    for b in boards:
        vals=b.get(key,()) if isinstance(b,dict) else getattr(b,key,())
        out.extend(float(x) for x in vals if x is not None)
    return out
