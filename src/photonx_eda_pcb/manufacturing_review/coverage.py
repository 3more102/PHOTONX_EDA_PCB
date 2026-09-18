def reconstruction_coverage(resolved,total):
    return 1.0 if total==0 else round(max(0,min(1,float(resolved)/float(total))),6)
