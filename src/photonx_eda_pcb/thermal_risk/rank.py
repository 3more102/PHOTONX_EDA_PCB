def rank_thermal(items):return sorted(items,key=lambda x:(-x.risk,-x.confidence,x.object_id))
