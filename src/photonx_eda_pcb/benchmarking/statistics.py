from statistics import mean,median,pstdev
def duration_stats(values):
    v=list(values)
    if not v:return {'count':0,'mean':None,'median':None,'min':None,'max':None,'pstdev':None}
    return {'count':len(v),'mean':mean(v),'median':median(v),'min':min(v),'max':max(v),'pstdev':pstdev(v)}
