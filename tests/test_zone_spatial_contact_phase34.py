from photonx_eda_pcb.models import PadCandidate,Track,Point
from photonx_eda_pcb.zones import Zone,ZoneIsland,zone_copper_contacts
from photonx_eda_pcb.zones.contact_report import zone_contact_report
def test_zone_contacts_exact_and_layer_filtered():
    z=Zone("Z","F.Cu","GND",[ZoneIsland("I",((0,0),(5,0),(5,5),(0,5)))])
    objs=[PadCandidate("P",Point(2,2),1,1,"C","F.Cu"),PadCandidate("B",Point(2,2),1,1,"C","B.Cu"),Track("T",Point(10,10),Point(11,10),.2,"F.Cu")]
    c=zone_copper_contacts(z,objs)
    assert c=={"I":("P",)}
    r=zone_contact_report(z,c)
    assert r["members"]==["P"] and r["isolated_islands"]==[]
