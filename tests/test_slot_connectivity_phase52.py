from photonx_eda_pcb.models import BoardModel,PadCandidate,Point
from photonx_eda_pcb.mechanical_features import SlotFeature
from photonx_eda_pcb.slot_connectivity import resolve_slot_connectivity,add_slot_layer_edges
from photonx_eda_pcb.multilayer import LayerConnectivityGraph,connected_components

def test_proven_plated_slot_connects_layers():
    s=SlotFeature("S",(0,0),(4,0),1,"plated")
    b=BoardModel(pads=[
      PadCandidate("F",Point(2,0),6,2,"O","F.Cu",net_id="N1"),
      PadCandidate("B",Point(2,0),6,2,"O","B.Cu",net_id="N1"),
    ],slots=[s])
    c=resolve_slot_connectivity(b,s)
    assert c.proven and not c.conflict and c.layers==("F.Cu","B.Cu")
    g=LayerConnectivityGraph();nodes=add_slot_layer_edges(g,c)
    assert nodes==("S@F.Cu","S@B.Cu")
    assert connected_components(g)==(("S@B.Cu","S@F.Cu"),)

def test_net_conflict_prevents_slot_layer_edge():
    s=SlotFeature("S",(0,0),(4,0),1,"plated")
    b=BoardModel(pads=[
      PadCandidate("F",Point(2,0),6,2,"O","F.Cu",net_id="N1"),
      PadCandidate("B",Point(2,0),6,2,"O","B.Cu",net_id="N2"),
    ],slots=[s])
    c=resolve_slot_connectivity(b,s)
    assert c.proven and c.conflict
    g=LayerConnectivityGraph();add_slot_layer_edges(g,c)
    assert g.neighbors("S@F.Cu")==()
