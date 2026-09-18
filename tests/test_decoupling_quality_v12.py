from photonx_eda_pcb.decoupling_quality import DecouplingObservation,analyze_decoupling,validate_decoupling_quality
from photonx_eda_pcb.decoupling_quality.domain import domain_quality
def test_decoupling_quality():
    q=analyze_decoupling([DecouplingObservation("C1","VDD","GND",1.0,100e-9),DecouplingObservation("C2","VDD","GND",5.0,1e-6)])
    assert len(q)==2 and all(validate_decoupling_quality(x)==[] for x in q)
    assert 0<domain_quality(q,"VDD")<=1
