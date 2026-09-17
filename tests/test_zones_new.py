from photonx_eda_pcb.zones.model import Zone,ZoneIsland
from photonx_eda_pcb.zones.analysis import zone_area,zone_bounds
from photonx_eda_pcb.zones.validation import validate_zone

def test_zone_area_bounds_and_validation():
    z=Zone('Z1','F.Cu',islands=[ZoneIsland('I1',((0,0),(2,0),(2,1),(0,1)))])
    assert zone_area(z)==2.0
    assert zone_bounds(z)==(0,0,2,1)
    assert validate_zone(z)==[]
