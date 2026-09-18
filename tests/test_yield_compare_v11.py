from photonx_eda_pcb.fabrication_yield.model import YieldRisk
from photonx_eda_pcb.fabrication_yield.compare import compare_yield
def test_yield_compare():
    d=compare_yield(YieldRisk(.2,"low"),YieldRisk(.5,"medium"))
    assert d["score_delta"]==.3 and d["level_after"]=="medium"
