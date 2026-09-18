from photonx_eda_pcb.netlist_reconstruction.model import Netlist,NetConnection
from photonx_eda_pcb.schematic_graph import build_schematic_graph
from photonx_eda_pcb.serial_endpoints import infer_serial_links,validate_serial_link
def test_i2c_endpoints():
    n=Netlist({"scl":[NetConnection("U1","1"),NetConnection("U2","1")],"sda":[NetConnection("U1","2"),NetConnection("U2","2")]},{"scl":"I2C_SCL","sda":"I2C_SDA"})
    g=build_schematic_graph(n)
    links=infer_serial_links(n.labels,g)
    i2c=[x for x in links if x.protocol=="I2C"][0]
    assert set(i2c.nets)=={"scl","sda"} and len({e.component_id for e in i2c.endpoints})==2
    assert validate_serial_link(i2c)==[]
