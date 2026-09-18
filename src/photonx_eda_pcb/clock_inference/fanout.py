def fanout_score(fanout):
    n=max(0,int(fanout))
    if n>=8:return .2
    if n>=4:return .12
    if n>=2:return .05
    return 0.0
