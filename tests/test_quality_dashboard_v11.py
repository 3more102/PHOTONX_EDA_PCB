from photonx_eda_pcb.quality_dashboard import build_dashboard,validate_dashboard
def test_dashboard():
    d=build_dashboard({"tests":{"score":1.0,"count":300},"si":.7,"dfm":.8})
    assert len(d.cards)==3 and 0<d.overall_score<=1
    assert validate_dashboard(d)==[]
