def validate_via_spans(spans):
    issues=[]
    for s in spans:
        if not 0<=s.confidence<=1:issues.append(('error','VIA_SPAN_CONFIDENCE',s.drill_id))
        if s.proven and (s.from_layer is None or s.to_layer is None):issues.append(('error','VIA_SPAN_PROVEN_WITHOUT_LAYERS',s.drill_id))
        if s.from_layer==s.to_layer and s.from_layer is not None:issues.append(('info','VIA_SINGLE_LAYER_EVIDENCE',s.drill_id))
    return issues
