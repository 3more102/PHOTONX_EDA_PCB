def run_fuzz_cases(cases,target):
    out=[]
    for c in cases:
        try:
            target(c.payload); out.append({'name':c.name,'status':'ok','exception':None})
        except Exception as e:
            out.append({'name':c.name,'status':'exception','exception':type(e).__name__})
    return out
