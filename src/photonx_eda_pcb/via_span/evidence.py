def span_evidence(drill,pads):
    ev=[f'drill {drill.id} overlaps {len(pads)} pad candidate(s)']
    layers=sorted({p.layer for p in pads})
    if layers:ev.append('observed layers: '+', '.join(layers))
    if drill.plating!='unknown':ev.append(f'plating metadata: {drill.plating}')
    span=getattr(drill,'layer_span',None)
    if span is not None:ev.append(f'explicit layer span metadata: {span!r}')
    if bool(getattr(drill,'span_proven',False)):ev.append('explicit layer span marked proven')
    return ev
