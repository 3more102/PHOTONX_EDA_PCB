from photonx_eda_pcb.board_variants.bom import variant_bom_items
from photonx_eda_pcb.bom_reconciliation import reconcile_bom
def reconcile_variant_bom(bom_items,components,variant):
    return reconcile_bom(variant_bom_items(bom_items,variant),components)
