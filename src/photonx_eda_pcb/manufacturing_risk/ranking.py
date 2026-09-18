def ranked_items(r):return sorted(r.items,key=lambda x:(-x.score,x.domain,x.code))
