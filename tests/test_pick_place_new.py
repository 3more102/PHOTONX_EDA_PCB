from photonx_eda_pcb.pick_place import read_pick_place_csv
from photonx_eda_pcb.pick_place.transform import transform_placement
def test_pick_place_ingestion_and_transform():
    placements=read_pick_place_csv('Reference,X,Y,Rotation,Side\nU1,10,20,90,Bottom\n')
    assert placements[0].side=='bottom' and placements[0].rotation==90
    moved=transform_placement(placements[0],scale=2,offset_x=1,offset_y=-1,rotation_offset=90)
    assert (moved.x,moved.y,moved.rotation)==(21,39,180)
