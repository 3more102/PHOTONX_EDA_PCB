from photonx_eda_pcb.design_rule_profiles import default_profile,resolve_profile,validate_profile
def test_rule_override():
    p=default_profile();p.net_overrides["VCC"]={"min_track_mm":.5}
    assert resolve_profile(p,"VCC")["min_track_mm"]==.5
    assert validate_profile(p)==[]
