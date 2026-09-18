from .model import LearnedRule,LearnedProfile
from .statistics import percentile
def _rule(name,values,p=.05):
    vals=[float(x) for x in values if x is not None and float(x)>0]
    if not vals:return None
    value=percentile(vals,p);confidence=min(1.0,len(vals)/20.0)
    return LearnedRule(name,round(value,6),round(confidence,6),len(vals))
def learn_rules(name,*,track_widths=(),clearances=(),drills=(),annular_rings=()):
    rules={}
    for key,vals in (("min_track_mm",track_widths),("min_clearance_mm",clearances),("min_drill_mm",drills),("min_annular_mm",annular_rings)):
        r=_rule(key,vals)
        if r:rules[key]=r
    return LearnedProfile(str(name),rules)
