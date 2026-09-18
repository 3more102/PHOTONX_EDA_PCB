from photonx_eda_pcb.netlist_reconstruction.model import Netlist,NetConnection
from photonx_eda_pcb.schematic_graph import build_schematic_graph
from photonx_eda_pcb.topology_analytics import build_net_component_graph
from photonx_eda_pcb.serial_endpoints import infer_serial_links
from photonx_eda_pcb.connector_paths import trace_connector_paths
from photonx_eda_pcb.supply_domains import partition_supply_domains
from photonx_eda_pcb.decoupling_quality import DecouplingObservation,analyze_decoupling
def test_phase12_topology_flow():
    n=Netlist({"scl":[NetConnection("J1","1"),NetConnection("U1","1")],"sda":[NetConnection("J1","2"),NetConnection("U1","2")],"vdd":[NetConnection("U1","3"),NetConnection("C1","1")],"gnd":[NetConnection("U1","4"),NetConnection("C1","2")]},{"scl":"I2C_SCL","sda":"I2C_SDA","vdd":"+3V3","gnd":"GND"})
    sg=build_schematic_graph(n);gg=build_net_component_graph(sg)
    assert infer_serial_links(n.labels,sg)[0].protocol=="I2C"
    assert trace_connector_paths(gg,["J1"],["U1"])
    assert partition_supply_domains(["+3V3"],["GND"],{"U1":{"3":"+3V3","4":"GND"},"C1":{"1":"+3V3","2":"GND"}})[0].components==("C1","U1")
    assert analyze_decoupling([DecouplingObservation("C1","+3V3","GND",1,100e-9)])
