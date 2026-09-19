from photonx_eda_pcb.drc.drill_copper_metrics import drill_copper_metrics
from photonx_eda_pcb.drc.mechanical_metrics import mechanical_clearance_metrics
from photonx_eda_pcb.drc.model import DrcConfig
from photonx_eda_pcb.models import BoardModel,CopperRegion,Point


def test_clearance_metrics_count_copper_regions():
    region=CopperRegion(
        "R1",
        (Point(0,0),Point(1,0),Point(1,1),Point(0,0)),
        "F.Cu",
    )
    board=BoardModel(regions=[region])

    assert drill_copper_metrics(board,DrcConfig())["copper_objects"]==1
    assert mechanical_clearance_metrics([],board)["copper_objects"]==1
