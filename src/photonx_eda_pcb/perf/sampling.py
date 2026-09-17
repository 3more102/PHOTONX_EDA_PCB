def deterministic_sample(items,limit):
    seq=list(items)
    if limit<0: raise ValueError("limit must be nonnegative")
    if len(seq)<=limit:return seq
    if limit==0:return []
    step=len(seq)/limit
    return [seq[min(int(index*step),len(seq)-1)] for index in range(limit)]
