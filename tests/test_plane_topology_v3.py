from photonx_eda_pcb.copper_plane_topology import PlaneIsland,build_plane_topology,validate_topology
from photonx_eda_pcb.copper_plane_topology.net_areas import net_areas
def test_plane_topology():
    t=build_plane_topology([PlaneIsland("a","F.Cu",10,"GND"),PlaneIsland("b","F.Cu",5,"GND")],[("a","b")])
    assert net_areas(t)["GND"]==15
    assert validate_topology(t)==[]
