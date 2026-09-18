def decoupling_candidates(component_kinds,component_pin_nets,power_nets,ground_nets):
    p=set(power_nets);g=set(ground_nets);out=[]
    for cid,kind in component_kinds.items():
        if "cap" not in str(kind).lower():continue
        nets={n for n in component_pin_nets.get(cid,{}).values() if n is not None}
        if nets&p and nets&g:out.append(cid)
    return sorted(out)
