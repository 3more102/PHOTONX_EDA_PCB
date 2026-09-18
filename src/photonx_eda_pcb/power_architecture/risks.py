def power_architecture_risks(a):
    risks=[]
    if not a.rails:risks.append("NO_SUPPLY_DOMAINS")
    for s in a.stages:
        if not s.input_rails or not s.output_rails:risks.append("INCOMPLETE_STAGE:"+s.component_id)
    return tuple(sorted(risks))
