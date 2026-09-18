def compare_nets(expected,actual):
    e={k:set(v) for k,v in expected.items()};a={k:set(v) for k,v in actual.items()}
    return {"missing":sorted(set(e)-set(a)),"extra":sorted(set(a)-set(e)),"mismatched":sorted(k for k in set(e)&set(a) if e[k]!=a[k])}
