def priority_for(kind,confidence=None):
    base={"unsupported_syntax":100,"connectivity_conflict":90,"net_merge":80,"component_hypothesis":50,"value_hypothesis":40}.get(str(kind),20)
    if confidence is not None:base+=int((1-float(confidence))*20)
    return base
