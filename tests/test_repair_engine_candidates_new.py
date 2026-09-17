from photonx_eda_pcb.repair_engine.gaps import gap_candidate
from photonx_eda_pcb.repair_engine.zero_area import zero_area_candidate
from photonx_eda_pcb.repair_engine.ranking import rank_candidates

def test_repair_candidates_are_ranked_conservatively():
    z=zero_area_candidate('z',0.0);g=gap_candidate('a','b',.01,.05)
    ranked=rank_candidates([g,z])
    assert ranked[0].kind=='remove_zero_area'
    assert not g.automatic
