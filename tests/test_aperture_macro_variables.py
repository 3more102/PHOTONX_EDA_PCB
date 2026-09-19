from photonx_eda_pcb.aperture_macros.variables import substitute


def test_substitute_keeps_undefined_longer_variable_intact():
    assert substitute("$10+$1", {"1": 2.5}) == "$10+2.5"


def test_substitute_replaces_exact_overlapping_variable_tokens():
    assert substitute("$10+$1", {"1": 2.5, "10": 7.0}) == "7.0+2.5"


def test_substitute_accepts_dollar_prefixed_variable_keys():
    assert substitute("$1+$2", {"$1": 3.0, "$2": 4.0}) == "3.0+4.0"
