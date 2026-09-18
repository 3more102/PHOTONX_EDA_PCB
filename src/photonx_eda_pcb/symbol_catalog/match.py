def match_symbol(catalog,*,kind=None,pin_count=None,reference_prefix=None):
    out=[]
    for e in catalog.all():
        score=0;reasons=[]
        if kind and e.kind==kind:score+=.5;reasons.append("kind")
        if pin_count is not None and len(e.pins)==int(pin_count):score+=.35;reasons.append("pin_count")
        if reference_prefix and e.reference_prefix==reference_prefix:score+=.15;reasons.append("reference_prefix")
        if score>0:out.append((round(score,12),e,reasons))
    return sorted(out,key=lambda x:(-x[0],x[1].name))
