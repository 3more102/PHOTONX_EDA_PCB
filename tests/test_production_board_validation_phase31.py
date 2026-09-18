from photonx_eda_pcb.models import BoardModel
from photonx_eda_pcb.production_board_validation import validate_production_board,ProductionValidationConfig
def test_empty_board_can_be_validated_under_relaxed_research_config():
    cfg=ProductionValidationConfig(require_outline=False,require_connectivity=False,min_provenance_coverage=0,max_drc_errors=0,max_erc_errors=0)
    r=validate_production_board(BoardModel(),cfg)
    assert r.passed and r.blockers==[]
