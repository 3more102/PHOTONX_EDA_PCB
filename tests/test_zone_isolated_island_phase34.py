from photonx_eda_pcb.zones import Zone,ZoneIsland,zone_copper_contacts
def test_zone_isolated_island():
    z=Zone("Z","F.Cu",None,[ZoneIsland("I",((0,0),(1,0),(1,1),(0,1)))])
    assert zone_copper_contacts(z,[])=={}
