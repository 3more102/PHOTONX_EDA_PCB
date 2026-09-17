from photonx_eda_pcb.net_semantics import candidates_from_label
from photonx_eda_pcb.net_semantics.conflicts import conflicting_names
from photonx_eda_pcb.net_semantics.selection import best_candidate
def test_net_semantic_candidates():
    explicit=candidates_from_label('N1','GND')
    assert explicit[0].confidence==1.0 and best_candidate(explicit).name=='GND'
    other=candidates_from_label('N1','VSS',source='pattern')
    assert conflicting_names(explicit+other)=={'N1':('GND','VSS')}
