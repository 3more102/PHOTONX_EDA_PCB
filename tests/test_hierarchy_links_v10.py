from photonx_eda_pcb.schematic_hierarchy.model import HierarchyResult,HierarchyBlock
from photonx_eda_pcb.schematic_hierarchy.links import inter_block_nets
def test_inter_block_net():
    r=HierarchyResult([HierarchyBlock("a","a",["U1"],["N"],.8,[]),HierarchyBlock("b","b",["J1"],["N"],.8,[])],[])
    assert inter_block_nets(r)=={"N":["a","b"]}
