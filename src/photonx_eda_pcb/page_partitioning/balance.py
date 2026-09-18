def partition_balance(parts):
    if not parts:return {"min":0,"max":0,"spread":0,"average":0.0}
    w=[p.weight for p in parts]
    return {"min":min(w),"max":max(w),"spread":max(w)-min(w),"average":round(sum(w)/len(w),6)}
