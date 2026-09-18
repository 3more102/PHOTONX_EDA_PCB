def decoupling_by_power_net(component_pin_nets,component_kinds,power_nets,ground_nets):
    p=set(power_nets);g=set(ground_nets);out={n:[] for n in p}
    for cid,pins in component_pin_nets.items():
        if "cap" not in str(component_kinds.get(cid,"")).lower():continue
        nets={n for n in pins.values() if n is not None}
        for n in nets&p:
            if nets&g:out.setdefault(n,[]).append(cid)
    return {k:sorted(v) for k,v in sorted(out.items())}
