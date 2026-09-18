from photonx_eda_pcb.architecture_decisions import ArchitectureDecision,DecisionStore,validate_decision
from photonx_eda_pcb.architecture_decisions.markdown import decision_markdown
def test_adr_store_and_markdown():
    d=ArchitectureDecision("ADR-001","Validation bridge","accepted","Multiple validators exist.","Normalize results through adapters.",("Preserve old APIs",))
    s=DecisionStore();s.add(d)
    assert s.get("ADR-001")==d and validate_decision(d)==[]
    assert "Validation bridge" in decision_markdown(d)
