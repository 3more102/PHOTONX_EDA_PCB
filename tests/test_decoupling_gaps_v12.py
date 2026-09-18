from photonx_eda_pcb.decoupling_quality import DecouplingObservation,analyze_decoupling
from photonx_eda_pcb.decoupling_quality.gaps import low_quality
def test_low_quality_decoupling():
    q=analyze_decoupling([DecouplingObservation("C1","VDD","GND",20.0,None)])
    assert low_quality(q,.6)
