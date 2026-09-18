from photonx_eda_pcb.rule_learning import learn_rules,validate_learned_profile
from photonx_eda_pcb.rule_learning.to_profile import learned_to_profile
def test_rule_learning():
    p=learn_rules("known",track_widths=[.15,.16,.2,.18]*6,clearances=[.15,.2,.18]*7,drills=[.3]*20,annular_rings=[.12]*20)
    assert p.rules["min_track_mm"].sample_count==24
    assert p.rules["min_track_mm"].confidence==1.0
    assert learned_to_profile(p).min_track_mm>0
    assert validate_learned_profile(p)==[]
