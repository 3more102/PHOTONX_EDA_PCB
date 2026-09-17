from photonx_eda_pcb.audit import AuditRecord,AuditTrail
def test_audit_trail_target_query():
    trail=AuditTrail(); trail.append(AuditRecord.create("infer","P1","pad hypothesis")); trail.append(AuditRecord.create("rename","N1","GND"))
    assert len(trail.all())==2 and trail.for_target("P1")[0].action=="infer"
