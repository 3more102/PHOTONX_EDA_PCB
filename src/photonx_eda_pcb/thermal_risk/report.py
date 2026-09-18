from .classify import risk_level
def thermal_report(items):return [{"object_id":x.object_id,"risk":x.risk,"level":risk_level(x.risk),"confidence":x.confidence,"evidence":list(x.evidence),"assumptions":list(x.assumptions)} for x in rank_items(items)]
def rank_items(items):return sorted(items,key=lambda x:(-x.risk,x.object_id))
