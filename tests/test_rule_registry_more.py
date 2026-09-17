import pytest
from photonx_eda_pcb.validation_rules.registry import RuleRegistry
def test_registry_order():
 r=RuleRegistry(); r.register('b',lambda b:['b']); r.register('a',lambda b:['a']); assert r.run(object())==['a','b']
def test_duplicate_rule():
 r=RuleRegistry(); r.register('a',lambda b:[]);
 with pytest.raises(ValueError): r.register('a',lambda b:[])
