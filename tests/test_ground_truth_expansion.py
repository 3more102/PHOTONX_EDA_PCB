from photonx_eda_pcb.models import BoardModel,PadCandidate,Point
from photonx_eda_pcb.ground_truth.model import GroundTruth
from photonx_eda_pcb.ground_truth.comparison import compare_board_truth
def test_truth():
    b=BoardModel(pads=[PadCandidate('p',Point(0,0),1,1,'C','F.Cu')]); t=GroundTruth({'pads':1}); assert compare_board_truth(b,t)['passed']
