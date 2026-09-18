from photonx_eda_pcb.protocol_detection.model import ProtocolCandidate
from photonx_eda_pcb.protocol_detection.diff_pairs import boost_with_diff_pairs
from photonx_eda_pcb.differential_pairs.model import PairCandidate
def test_diff_pair_boost():
    c=[ProtocolCandidate("usb",("p","n"),.9,("net_labels",))]
    p=[PairCandidate("p","n",.9,())]
    assert boost_with_diff_pairs(c,p)[0].confidence==.95
