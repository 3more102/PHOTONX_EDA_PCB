def span_evidence(drill,pads):
    ev=[f'drill {drill.id} overlaps {len(pads)} pad candidate(s)']
    layers=sorted({p.layer for p in pads})
    if layers:ev.append('observed layers: '+', '.join(layers))
    if drill.plating!='unknown':ev.append(f'plating metadata: {drill.plating}')
    return ev
