from collections import Counter
from .model import PatternMatch
def _score(pattern,kinds,roles):
    kc=Counter(str(x).lower() for x in kinds);required=Counter(str(x).lower() for x in pattern.required_kinds)
    if any(kc[k]<n for k,n in required.items()):return 0.0,()
    count=sum(kc.values())
    if count<pattern.min_components or (pattern.max_components is not None and count>pattern.max_components):return 0.0,()
    role_set={str(x).lower() for x in roles};req_roles={str(x).lower() for x in pattern.required_roles}
    if not req_roles.issubset(role_set):return 0.0,()
    base=.65+.2*(len(required)/max(1,len(kc)))+.15*(len(req_roles)/max(1,len(role_set))) if req_roles else .75+.2*(len(required)/max(1,len(kc)))
    return round(min(base,1),6),("component_kinds",)+(("net_roles",) if req_roles else ())
def match_patterns(library,object_id,kinds,roles=()):
    out=[]
    for p in library.all():
        score,ev=_score(p,kinds,roles)
        if score>0:out.append(PatternMatch(p.name,str(object_id),score,ev))
    return sorted(out,key=lambda x:(-x.score,x.pattern))
