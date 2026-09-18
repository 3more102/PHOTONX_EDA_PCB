from photonx_eda_pcb.quality_dashboard import build_dashboard
from photonx_eda_pcb.quality_dashboard.trend import dashboard_delta
def test_dashboard_delta():
    a=build_dashboard({"x":.5});b=build_dashboard({"x":.8})
    assert dashboard_delta(a,b)==.3
