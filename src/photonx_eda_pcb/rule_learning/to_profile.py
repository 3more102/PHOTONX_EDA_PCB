from photonx_eda_pcb.design_rule_profiles.model import RuleProfile
def learned_to_profile(lp,default_name=None):
    vals={k:r.value for k,r in lp.rules.items()}
    return RuleProfile(default_name or lp.name,vals.get("min_track_mm",.15),vals.get("min_clearance_mm",.15),vals.get("min_drill_mm",.2),vals.get("min_annular_mm",.1),.1,{})
