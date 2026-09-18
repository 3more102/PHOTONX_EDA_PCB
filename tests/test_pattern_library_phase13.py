from photonx_eda_pcb.pattern_library.library import PatternLibrary
from photonx_eda_pcb.pattern_library.defaults import default_patterns
from photonx_eda_pcb.pattern_library import match_patterns
def test_led_pattern_match():
    lib=PatternLibrary(default_patterns())
    m=match_patterns(lib,"x",["resistor","led"],[])
    assert m and m[0].pattern=="led_resistor_channel"
