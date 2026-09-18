from photonx_eda_pcb.models import BoardModel
from photonx_eda_pcb.mechanical_features import SlotFeature
from photonx_eda_pcb.production_board_validation import validate_production_board,ProductionValidationConfig

def relaxed(**kwargs):
    d=dict(require_outline=False,require_connectivity=False,min_provenance_coverage=0,max_drc_errors=99,max_erc_errors=99)
    d.update(kwargs);return ProductionValidationConfig(**d)

def test_unknown_slot_plating_blocks_production_by_default():
    r=validate_production_board(BoardModel(slots=[SlotFeature("S",(0,0),(1,0),.5,"unknown")]),relaxed())
    assert "PRODUCTION_SLOT_PLATING_UNKNOWN" in r.blockers

def test_nonplated_slot_can_pass_plating_gate():
    r=validate_production_board(BoardModel(slots=[SlotFeature("S",(0,0),(1,0),.5,"non-plated")]),relaxed())
    assert "PRODUCTION_SLOT_PLATING_UNKNOWN" not in r.blockers

def test_plated_slot_blocks_when_kicad_exportability_required():
    r=validate_production_board(BoardModel(slots=[SlotFeature("S",(0,0),(1,0),.5,"plated")]),relaxed(require_kicad_exportable_slots=True))
    assert "PRODUCTION_PLATED_SLOT_PADSTACK_REQUIRED" in r.blockers
