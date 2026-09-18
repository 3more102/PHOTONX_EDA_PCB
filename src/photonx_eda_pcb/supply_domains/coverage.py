def domain_coverage(domains,components):
    covered=set(c for d in domains for c in d.components);allc=set(map(str,components))
    return 1.0 if not allc else round(len(covered&allc)/len(allc),6)
