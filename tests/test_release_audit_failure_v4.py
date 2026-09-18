from photonx_eda_pcb.release_audit import run_release_audit,audit_passed
from photonx_eda_pcb.release_audit.decision import failed_checks
def test_release_audit_blocks():
    a=run_release_audit(tests_passed=True,unsupported_count=2,critical_findings=0,deterministic=True,provenance_complete=True)
    assert not audit_passed(a) and "unsupported_syntax" in failed_checks(a)
