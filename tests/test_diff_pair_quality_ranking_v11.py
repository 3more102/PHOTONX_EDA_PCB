from photonx_eda_pcb.differential_pair_quality import analyze_pair_quality
from photonx_eda_pcb.differential_pair_quality.ranking import weakest_pairs
def test_weakest_pair_first():
    a=analyze_pair_quality("A_P","A_N",skew_mm=.01);b=analyze_pair_quality("B_P","B_N",skew_mm=1)
    assert weakest_pairs([a,b])[0].positive_net=="B_P"
