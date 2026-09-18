from photonx_eda_pcb.functional_blocks.model import FunctionalBlock
from photonx_eda_pcb.page_partitioning import partition_blocks,validate_partitions
from photonx_eda_pcb.page_partitioning.balance import partition_balance
def test_partition_blocks_deterministic():
    blocks=[FunctionalBlock("b1",("U1","U2"),("N1",),"compute",.8),FunctionalBlock("b2",("J1",),("N1","N2"),"interface",.8),FunctionalBlock("b3",("U3","U4"),("N3",),"sensor",.7)]
    p=partition_blocks(blocks,max_components=3)
    assert len(p)==2 and validate_partitions(p)==[]
    assert partition_balance(p)["spread"]<=1
