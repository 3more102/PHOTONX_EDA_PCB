def oscillator_support_summary(items):return {"candidates":len(items),"with_grounded_caps":sum(dict(x.parameters).get("grounded_capacitors",0)>0 for x in items)}
