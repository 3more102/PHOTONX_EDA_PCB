from photonx_eda_pcb.pick_place.model import Placement
from photonx_eda_pcb.centroid_export import from_placements,write_centroid_csv,validate_centroids
def test_centroid_csv_deterministic():
    r=from_placements([Placement("R2",2,0),Placement("R1",1,0)])
    text=write_centroid_csv(r)
    assert text.splitlines()[1].startswith("R1,")
    assert validate_centroids(r)==[]
