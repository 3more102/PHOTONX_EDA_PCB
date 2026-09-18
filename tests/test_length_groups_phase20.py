from photonx_eda_pcb.bus_grouping.model import BusCandidate
from photonx_eda_pcb.differential_pairs.model import PairCandidate
from photonx_eda_pcb.length_groups import build_length_groups,validate_length_group
from photonx_eda_pcb.length_groups.skew import group_skew,within_group_tolerance
def test_length_groups_bus_and_diff():
    bus=BusCandidate("D",("d0","d1"),(0,1),2,.8)
    pair=PairCandidate("p","n",.9,())
    groups=build_length_groups([bus],[pair],{"d0":10,"d1":10.1,"p":20,"n":20.05})
    assert len(groups)==2 and all(validate_length_group(g)==[] for g in groups)
    bg=[g for g in groups if g.kind=="bus"][0]
    assert group_skew(bg,{"d0":10,"d1":10.1})==.1 and within_group_tolerance(bg,{"d0":10,"d1":10.1})
