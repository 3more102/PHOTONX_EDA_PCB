from photonx_eda_pcb.component_neighborhood.model import ComponentNeighborhood
from photonx_eda_pcb.component_neighborhood.similarity import neighborhood_similarity
def test_similarity_bounds():
    a=ComponentNeighborhood("A",("N1",),("B","C"),2,())
    b=ComponentNeighborhood("D",("N1",),("B","C"),2,())
    assert neighborhood_similarity(a,b)==1.0
