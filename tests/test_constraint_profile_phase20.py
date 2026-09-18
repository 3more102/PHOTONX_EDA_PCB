from photonx_eda_pcb.constraint_synthesis import synthesize_constraints
from photonx_eda_pcb.constraint_synthesis.profile import to_rule_profile
def test_constraint_profile_overrides():
    s=synthesize_constraints(["v"],{"v":("power",)})
    p=to_rule_profile("generated",s)
    assert p.net_overrides["v"]["min_track_mm"]==.3
