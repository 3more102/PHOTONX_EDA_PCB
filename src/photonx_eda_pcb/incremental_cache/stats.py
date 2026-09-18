def cache_stats(cache):
    total=cache.hits+cache.misses
    return {"entries":len(cache),"hits":cache.hits,"misses":cache.misses,"hit_rate":0.0 if total==0 else round(cache.hits/total,6)}
