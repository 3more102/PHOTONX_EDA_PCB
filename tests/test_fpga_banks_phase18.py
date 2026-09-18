from photonx_eda_pcb.fpga_banks import build_fpga_banks,validate_fpga_bank
from photonx_eda_pcb.fpga_banks.io_standards import io_standard_conflicts,voltage_conflicts
def test_fpga_bank_build():
    banks=build_fpga_banks("U1",{"A1":{"bank":"13","net_id":"N1","io_standard":"LVCMOS33","voltage":3.3},"A2":{"bank":"13","net_id":"N2","io_standard":"LVCMOS33","voltage":3.3}})
    assert len(banks)==1 and banks[0].bank=="13" and banks[0].supply_voltage==3.3
    assert io_standard_conflicts(banks[0])==[] and not voltage_conflicts(banks[0])
    assert validate_fpga_bank(banks[0])==[]
