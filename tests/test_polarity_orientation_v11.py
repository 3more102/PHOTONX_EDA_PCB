from photonx_eda_pcb.polarity_orientation import infer_polarity,infer_orientation,validate_polarity,validate_orientation
def test_led_polarity_and_orientation():
    p=infer_polarity("D1",{"1":"K","2":"A"})
    assert p.positive_pin=="2" and p.negative_pin=="1" and validate_polarity(p)==[]
    o=infer_orientation("D1",450,"1",True)
    assert o.rotation_deg==90 and o.confidence==.9 and validate_orientation(o)==[]
