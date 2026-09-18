def length_report(lengths):
    return [{"net":k,"length_mm":round(float(v),6)} for k,v in sorted(lengths.items())]
