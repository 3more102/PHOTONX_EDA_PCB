from photonx_eda_pcb.copper_plane_topology import PlaneIsland,build_plane_topology
from photonx_eda_pcb.copper_plane_topology.orphans import orphan_islands
def test_plane_orphan():
    t=build_plane_topology([PlaneIsland("a","F.Cu",1,None)])
    assert orphan_islands(t)==["a"]
