from photonx_eda_pcb.decoupling_quality.model import DecouplingObservation,DecouplingQuality
from photonx_eda_pcb.decoupling_groups import group_decoupling,validate_group
def test_decoupling_group_bulk_and_total():
    obs=[DecouplingObservation("C1","VDD","GND",1,100e-9),DecouplingObservation("C2","VDD","GND",2,10e-6)]
    q=[DecouplingQuality("C1","VDD",.8,.8),DecouplingQuality("C2","VDD",.9,.9)]
    g=group_decoupling(obs,q)[0]
    assert g.bulk_components==("C2",) and g.total_capacitance_f>10e-6
    assert validate_group(g)==[]
