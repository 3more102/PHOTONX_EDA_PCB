def skew_matrix(lengths):
    names=sorted(lengths)
    return {(a,b):abs(float(lengths[a])-float(lengths[b])) for i,a in enumerate(names) for b in names[i+1:]}
