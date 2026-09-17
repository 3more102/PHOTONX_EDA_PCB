def classify_span(layers:list[str],stackup)->str:
    names=[x.name for x in stackup.copper_layers()]
    hits=sorted(set(x for x in layers if x in names),key=names.index if names else None)
    if len(hits)<2:return 'unknown'
    if hits[0]==names[0] and hits[-1]==names[-1]:return 'through'
    if hits[0] in {names[0],names[-1]} or hits[-1] in {names[0],names[-1]}:return 'blind'
    return 'buried'
