def field_accuracy(cases,field):
    total=0;ok=0
    for c in cases:
        if field in c.expected:
            total+=1;ok+=field in c.observed and c.observed[field]==c.expected[field]
    return None if total==0 else round(ok/total,6)
