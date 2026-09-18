from photonx_eda_pcb.functional_blocks.model import FunctionalBlock
from photonx_eda_pcb.functional_blocks.coverage import block_coverage
def test_block_coverage():
    b=[FunctionalBlock("b",("A","B"),(),"unknown",.5)]
    assert block_coverage(b,["A","B","C"])==round(2/3,6)
