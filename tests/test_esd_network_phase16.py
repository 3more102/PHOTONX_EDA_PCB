from photonx_eda_pcb.protection_inference.model import ProtectionCandidate
from photonx_eda_pcb.esd_networks import infer_esd_networks,validate_esd_network
def test_esd_network_to_ground():
    p=ProtectionCandidate("D1","esd",("USB_DP","GND"),.9,(),())
    n=infer_esd_networks([p],["GND"],["USB_DP"])[0]
    assert n.interface_net=="USB_DP" and n.ground_nets==("GND",)
    assert validate_esd_network(n)==[]
