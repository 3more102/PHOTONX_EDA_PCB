from photonx_eda_pcb.mechanical_features import SlotFeature
from photonx_eda_pcb.mechanical_features.export_readiness import assess_slot_export_readiness

def test_slot_export_readiness_categories():
    r=assess_slot_export_readiness([
      SlotFeature("N",(0,0),(1,0),.5,"non-plated"),
      SlotFeature("U",(0,1),(1,1),.5,"unknown"),
      SlotFeature("P",(0,2),(1,2),.5,"plated"),
    ])
    assert r.exportable_npth==("N",)
    assert r.unknown_plating==("U",)
    assert r.plated_without_padstack==("P",)
    assert not r.fully_resolved
