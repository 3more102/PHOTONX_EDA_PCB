from photonx_eda_pcb.power_distribution import copper_resistance,estimated_drop
from photonx_eda_pcb.power_distribution.current_density import current_density_a_per_mm2
def test_pdn_math():
    r=copper_resistance(100,1,35)
    assert 0<r<1
    assert estimated_drop(1,r)==r
    assert current_density_a_per_mm2(1,1,35)>0
