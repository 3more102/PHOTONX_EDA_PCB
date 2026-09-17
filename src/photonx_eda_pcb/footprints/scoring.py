def score_signature(features,sig):
    if features['count']!=sig.get('pad_count'):return 0.0
    score=0.55; drilled=features['drilled_fraction']
    if 'drilled_min' in sig: score += 0.25 if drilled>=sig['drilled_min'] else -0.25
    if 'drilled_max' in sig: score += 0.25 if drilled<=sig['drilled_max'] else -0.25
    x0,y0,x1,y1=features['bbox']; w=max(x1-x0,1e-9); h=max(y1-y0,1e-9); aspect=max(w/h,h/w)
    if aspect>=sig.get('aspect_min',1):score+=0.15
    return max(0.0,min(1.0,score))
