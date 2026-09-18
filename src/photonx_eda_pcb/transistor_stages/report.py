def transistor_stage_summary(items):return {"candidates":len(items),"with_bias":sum("control_bias_resistor" in x.evidence for x in items)}
