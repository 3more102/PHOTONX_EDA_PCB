from photonx_eda_pcb.release_evidence import assemble_release_evidence
class I: severity="warning"
def test_release_evidence_counts():
    e=assemble_release_evidence(issues=[I(),{"severity":"error"}],metrics={"completeness":.9})
    assert e.issue_counts=={"warning":1,"error":1}
