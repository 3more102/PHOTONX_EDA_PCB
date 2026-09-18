from photonx_eda_pcb.design_rule_profiles import default_profile
from photonx_eda_pcb.design_rule_profiles.apply import violations_for_track
class T: width=.1;net_id=None
def test_track_violation():
    assert violations_for_track(T(),default_profile())==["TRACK_WIDTH"]
