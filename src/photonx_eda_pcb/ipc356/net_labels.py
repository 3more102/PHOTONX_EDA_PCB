def net_labels(evidence):
    out={}
    for e in evidence:
        out.setdefault(e.pad_id,e.net_name)
    return out
