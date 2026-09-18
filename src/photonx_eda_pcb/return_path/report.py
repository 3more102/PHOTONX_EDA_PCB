from .risk import return_path_risk
def return_path_report(e):return {"net_id":e.net_id,"reference_plane":e.reference_plane,"continuity_score":e.continuity_score,"via_penalty":e.via_penalty,"split_crossings":e.split_crossings,"confidence":e.confidence,"risk":return_path_risk(e),"evidence":list(e.evidence)}
