def compare_benchmarks(before,after):
    b=float(before.median_seconds);a=float(after.median_seconds)
    ratio=None if b<=0 else a/b
    return {"name":after.name,"before_seconds":b,"after_seconds":a,"ratio":ratio,"improved":None if ratio is None else ratio<1.0}
