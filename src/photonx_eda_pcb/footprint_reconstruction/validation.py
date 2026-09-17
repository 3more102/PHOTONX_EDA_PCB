def validate_reconstruction(fp):
    issues=[]
    if not fp.id:issues.append('FOOTPRINT_ID_EMPTY')
    if not fp.pad_ids:issues.append('FOOTPRINT_NO_PADS')
    if not 0<=fp.confidence<=1:issues.append('FOOTPRINT_CONFIDENCE_RANGE')
    if len(fp.pad_ids)!=len(set(fp.pad_ids)):issues.append('FOOTPRINT_DUPLICATE_PAD')
    return issues
