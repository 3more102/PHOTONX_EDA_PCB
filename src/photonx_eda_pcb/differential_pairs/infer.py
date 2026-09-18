from .model import PairCandidate
from .naming import complementary_name
def infer_pairs(nets,lengths=None,max_relative_mismatch=0.15):
    names=sorted(str(n) for n in nets); lengths=lengths or {};out=[]
    for i,a in enumerate(names):
        for b in names[i+1:]:
            reasons=[];score=0.0
            if complementary_name(a,b):score+=0.65;reasons.append("complementary_name")
            if a in lengths and b in lengths:
                m=max(float(lengths[a]),float(lengths[b]),1e-12)
                rel=abs(float(lengths[a])-float(lengths[b]))/m
                if rel<=max_relative_mismatch:score+=0.25;reasons.append("length_match")
            if score>=0.65:
                out.append(PairCandidate(a,b,round(min(score,1),12),tuple(reasons)))
    return out
