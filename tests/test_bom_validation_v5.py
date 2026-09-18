from photonx_eda_pcb.bom_reconciliation import BomRecord
from photonx_eda_pcb.bom_reconciliation.validation import validate_bom_records
def test_duplicate_bom_ref():
    assert "BOM_REFERENCE_DUPLICATE" in validate_bom_records([BomRecord("R1"),BomRecord("r1")])
