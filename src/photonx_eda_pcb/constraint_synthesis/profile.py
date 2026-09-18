from photonx_eda_pcb.design_rule_profiles.model import RuleProfile
def to_rule_profile(name,constraint_set):
    p=RuleProfile(str(name))
    for c in constraint_set.constraints:
        o={}
        if c.min_width_mm is not None:o["min_track_mm"]=c.min_width_mm
        if c.clearance_mm is not None:o["min_clearance_mm"]=c.clearance_mm
        if o:p.net_overrides[c.net_id]=o
    return p
