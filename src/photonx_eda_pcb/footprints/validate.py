def validate_candidates(candidates,board):
    pads={p.id for p in board.pads}; issues=[]
    for c in candidates:
        if not c.pad_ids:issues.append(('warning','FOOTPRINT_NO_PADS',c.id))
        if any(p not in pads for p in c.pad_ids):issues.append(('error','FOOTPRINT_PAD_MISSING',c.id))
        if not 0<=c.confidence<=1:issues.append(('error','FOOTPRINT_CONFIDENCE',c.id))
    return issues
