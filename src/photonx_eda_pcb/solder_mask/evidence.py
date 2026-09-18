def mask_confidence(has_pad_geometry=True,has_source_mask=False,shape_match=False):
    score=0.45 if has_pad_geometry else 0.0
    score+=0.4 if has_source_mask else 0.0
    score+=0.15 if shape_match else 0.0
    return round(min(score,1.0),12)
