from photonx_eda_pcb.copper_plane_topology import PlaneIsland,build_plane_topology
from photonx_eda_pcb.copper_plane_topology.reference_planes import reference_plane_candidates
from photonx_eda_pcb.controlled_impedance import ImpedanceConstraint,check_constraint
def test_plane_reference_and_constraint():
    t=build_plane_topology([PlaneIsland("g","B.Cu",120,"GND")])
    assert reference_plane_candidates(t,50)[0].net_id=="GND"
    assert check_constraint(ImpedanceConstraint("CLK",50,5),52,.8).passed is True
