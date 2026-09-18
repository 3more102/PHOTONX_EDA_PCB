from .quality import transition_quality
def transition_report(v,total_layers=2):return {"id":v.id,"net_id":v.net_id,"start_layer":v.start_layer,"end_layer":v.end_layer,"quality":transition_quality(v,total_layers),"confidence":v.confidence,"evidence":list(v.evidence)}
