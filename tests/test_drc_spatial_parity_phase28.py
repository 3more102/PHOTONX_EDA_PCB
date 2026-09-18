from photonx_eda_pcb.models import BoardModel,PadCandidate,Point
from photonx_eda_pcb.drc.model import DrcConfig
from photonx_eda_pcb.drc.clearance import check_clearance,check_clearance_bruteforce
def test_drc_spatial_matches_bruteforce():
    pads=[
      PadCandidate("A",Point(0,0),1,1,"C","F.Cu",net_id="N1"),
      PadCandidate("B",Point(1.05,0),1,1,"C","F.Cu",net_id="N2"),
      PadCandidate("C",Point(5,0),1,1,"C","F.Cu",net_id="N3"),
    ]
    b=BoardModel(pads=pads);cfg=DrcConfig(min_clearance_mm=.1)
    a=check_clearance_bruteforce(b,cfg);s=check_clearance(b,cfg)
    assert [(x.code,x.object_ids) for x in a]==[(x.code,x.object_ids) for x in s]
    assert len(s)==1
