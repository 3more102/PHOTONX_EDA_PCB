import pytest
from photonx_eda_pcb.repair_engine.candidate import RepairCandidate
from photonx_eda_pcb.repair_engine.policy import RepairPolicy
from photonx_eda_pcb.repair_engine.apply import plan_repairs,apply_repairs

def test_repair_application_is_disabled_by_default():
    c=RepairCandidate('remove_zero_area',('x',),1.0,'test',True)
    p=plan_repairs([c],RepairPolicy())
    assert not p['approved'] and p['review']==[c]
    with pytest.raises(RuntimeError):apply_repairs()
