from photonx_eda_pcb.schematic_pages.model import SchematicPage,SchematicPageSet
from photonx_eda_pcb.schematic_pages.crossrefs import cross_page_nets
def test_cross_page_nets():
    ps=SchematicPageSet([SchematicPage("a","A",("U1",),("N1",)),SchematicPage("b","B",("U2",),("N1","N2"))])
    assert cross_page_nets(ps)=={"N1":("a","b")}
