from photonx_eda_pcb.release_audit import run_release_audit,audit_passed
from photonx_eda_pcb.release_audit.score import audit_score
def test_release_audit():
    a=run_release_audit(tests_passed=True,unsupported_count=0,critical_findings=0,deterministic=True,provenance_complete=True)
    assert audit_passed(a) and audit_score(a)==1.0
