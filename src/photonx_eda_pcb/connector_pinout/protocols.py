def compatible_protocols(pinout,protocols):
    nets={p.net_id for p in pinout.pins if p.net_id}
    return [x for x in protocols if set(x.net_ids).issubset(nets)]
