from photonx_eda_pcb.fpga_banks import build_fpga_banks
from photonx_eda_pcb.fpga_banks.io_standards import io_standard_conflicts,voltage_conflicts
def test_fpga_bank_conflicts_visible():
    b=build_fpga_banks("U1",{"A1":{"bank":"1","io_standard":"LVCMOS33","voltage":3.3},"A2":{"bank":"1","io_standard":"LVCMOS18","voltage":1.8}})[0]
    assert len(io_standard_conflicts(b))==2 and voltage_conflicts(b)
