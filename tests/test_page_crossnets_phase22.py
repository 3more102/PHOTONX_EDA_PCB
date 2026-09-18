from photonx_eda_pcb.page_partitioning.model import PagePartition
from photonx_eda_pcb.page_partitioning.cross_nets import cross_partition_nets
def test_cross_partition_nets():
    p=[PagePartition("p1","A",(),("U1",),("N1","N2"),1),PagePartition("p2","B",(),("U2",),("N1","N3"),1)]
    assert cross_partition_nets(p)=={"N1":("p1","p2")}
