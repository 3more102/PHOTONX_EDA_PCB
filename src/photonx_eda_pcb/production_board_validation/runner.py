from photonx_eda_pcb.validation import validate_board
from photonx_eda_pcb.drc.engine import run_drc
from photonx_eda_pcb.erc.engine import run_erc
from photonx_eda_pcb.analysis.provenance_metrics import source_coverage
from photonx_eda_pcb.mechanical_features.export_readiness import assess_board_slot_export_readiness
from .model import ProductionValidationResult,ProductionValidationConfig

def validate_production_board(board,cfg=None,drc_cfg=None):
    cfg=cfg or ProductionValidationConfig();core=validate_board(board);drc=run_drc(board,drc_cfg);erc=run_erc(board)
    blockers=[];warnings=[];core_errors=len(core.errors);core_warnings=len(core.warnings)
    drc_errors=sum(x.severity=="error" for x in drc);erc_errors=sum(x.severity=="error" for x in erc);coverage=source_coverage(board)
    readiness=assess_board_slot_export_readiness(board)
    if cfg.require_outline and not board.outline:blockers.append("PRODUCTION_OUTLINE_REQUIRED")
    if cfg.require_connectivity and (board.pads or board.tracks) and not board.nets:blockers.append("PRODUCTION_CONNECTIVITY_REQUIRED")
    if core_errors:blockers.append("PRODUCTION_CORE_VALIDATION_ERRORS")
    if drc_errors>cfg.max_drc_errors:blockers.append("PRODUCTION_DRC_ERRORS")
    if erc_errors>cfg.max_erc_errors:blockers.append("PRODUCTION_ERC_ERRORS")
    if coverage<cfg.min_provenance_coverage:blockers.append("PRODUCTION_PROVENANCE_COVERAGE")
    if cfg.require_known_slot_plating and readiness.unknown_plating:blockers.append("PRODUCTION_SLOT_PLATING_UNKNOWN")
    if cfg.require_kicad_exportable_slots and readiness.plated_without_padstack:blockers.append("PRODUCTION_PLATED_SLOT_PADSTACK_REQUIRED")
    if core_warnings:warnings.append("PRODUCTION_CORE_WARNINGS")
    metrics={"core_errors":core_errors,"core_warnings":core_warnings,"drc_errors":drc_errors,"erc_errors":erc_errors,"provenance_coverage":coverage,"slots":len(getattr(board,"slots",())),"slot_unknown_plating":len(readiness.unknown_plating),"slot_exportable_npth":len(readiness.exportable_npth),"slot_exportable_plated":len(readiness.exportable_plated),"slot_plated_without_padstack":len(readiness.plated_without_padstack)}
    return ProductionValidationResult(not blockers,blockers,warnings,metrics)
