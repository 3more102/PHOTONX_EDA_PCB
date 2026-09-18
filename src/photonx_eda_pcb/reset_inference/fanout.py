def reset_fanout_boost(n):
    n=max(0,int(n))
    return .15 if n>=5 else (.08 if n>=2 else 0.0)
