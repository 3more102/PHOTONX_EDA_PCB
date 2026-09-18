from photonx_eda_pcb.board_variants.placements import variant_placements
from photonx_eda_pcb.placement_reconciliation import reconcile_placements
def reconcile_variant_placements(source,reconstructed,variant,**kwargs):
    return reconcile_placements(variant_placements(source,variant),variant_placements(reconstructed,variant),**kwargs)
