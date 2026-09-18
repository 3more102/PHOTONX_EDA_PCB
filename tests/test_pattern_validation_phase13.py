from photonx_eda_pcb.pattern_library.model import PatternDefinition
from photonx_eda_pcb.pattern_library.validation import validate_pattern
def test_invalid_pattern_bounds():
    assert "PATTERN_MAX_LT_MIN" in validate_pattern(PatternDefinition("x",(),3,2))
