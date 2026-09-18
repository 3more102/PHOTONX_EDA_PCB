from photonx_eda_pcb.differential_pair_quality import analyze_pair_quality,validate_pair_quality
def test_good_pair_quality():
    q=analyze_pair_quality("USB_P","USB_N",skew_mm=.05,spacing_variation_mm=.02,via_mismatch=0,confidence=.9)
    assert q.score>.8 and validate_pair_quality(q)==[]
def test_bad_pair_quality_notes():
    q=analyze_pair_quality("P","N",skew_mm=1.0,spacing_variation_mm=.3,via_mismatch=2)
    assert "high_skew" in q.notes and "spacing_variation" in q.notes and "via_mismatch" in q.notes
