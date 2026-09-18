def boost_with_diff_pairs(candidates,pairs):
    pair_sets=[{p.positive_net,p.negative_net} for p in pairs]
    out=[]
    for c in candidates:
        score=c.confidence;ev=list(c.evidence)
        if any(ps.issubset(set(c.net_ids)) for ps in pair_sets):score=min(1,score+.05);ev.append("differential_pair")
        out.append(type(c)(c.protocol,c.net_ids,round(score,12),tuple(ev)))
    return out
