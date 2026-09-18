from photonx_eda_pcb.bus_grouping import infer_buses
from photonx_eda_pcb.clock_inference import infer_clock_nets
from photonx_eda_pcb.reset_inference import infer_reset_nets
from photonx_eda_pcb.protocol_detection.model import ProtocolCandidate
from photonx_eda_pcb.signal_role_synthesis import synthesize_roles
def test_signal_semantics_integration():
    buses=infer_buses({"d0":"DATA0","d1":"DATA1"})
    clocks=infer_clock_nets([{"net_id":"clk","label":"SYSCLK","fanout":6}])
    resets=infer_reset_nets([{"net_id":"rst","label":"RESET_N","fanout":3}])
    protocols=[ProtocolCandidate("SPI",("clk","d0"),.7,("labels",))]
    roles=synthesize_roles(["clk","rst","d0","d1"],clock=clocks,reset=resets,buses=buses,protocols=protocols)
    by={x.net_id:set(x.roles) for x in roles}
    assert "clock" in by["clk"] and "protocol:SPI" in by["clk"]
    assert "reset" in by["rst"] and "bus:DATA" in by["d0"]
