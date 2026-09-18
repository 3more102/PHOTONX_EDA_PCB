from photonx_eda_pcb.geometry_kernel import quantize_value,quantize_point,GeometryTolerance
def test_decimal_quantization_is_deterministic():
    assert quantize_value(0.30000000000004,1e-3)==.3
    assert quantize_point(1.23456,2.34567,1e-3)==(1.235,2.346)
    assert GeometryTolerance().validate()==[]
