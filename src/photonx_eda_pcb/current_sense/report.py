def current_sense_summary(items):return {"candidates":len(items),"direct_identity":sum("shunt_identity" in x.evidence for x in items)}
