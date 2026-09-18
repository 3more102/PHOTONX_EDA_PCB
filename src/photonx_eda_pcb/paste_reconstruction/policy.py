def should_generate_paste(drill,layer):
    return drill in (None,0) and str(layer).lower() not in {"edge.cuts","drill"}
