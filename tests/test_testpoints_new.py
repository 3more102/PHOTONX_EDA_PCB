from types import SimpleNamespace
from photonx_eda_pcb.testpoints.detection import detect_testpoints
from photonx_eda_pcb.testpoints.coverage import net_coverage
from photonx_eda_pcb.testpoints.ranking import rank_testpoints

def test_testpoint_detection_and_coverage():
    objs=[SimpleNamespace(id='p1',diameter_mm=1.0,exposed=True,net_id='N1'),SimpleNamespace(id='p2',diameter_mm=.4,exposed=True,net_id='N2')]
    t=detect_testpoints(objs)
    assert [x.object_id for x in rank_testpoints(t)]==['p1']
    assert net_coverage(t,['N1','N2'])['covered']==1
