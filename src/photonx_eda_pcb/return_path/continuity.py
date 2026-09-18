def continuity_score(samples):
    vals=[1.0 if bool(x) else 0.0 for x in samples]
    return 0.0 if not vals else round(sum(vals)/len(vals),6)
