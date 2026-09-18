from .model import ManufacturingAudit
def audit_manufacturing_package(package_assessment,production_validation=None,traceability=None,fidelity=None):
    blockers=list(package_assessment.blockers);warnings=list(package_assessment.warnings);metrics={}
    if production_validation is not None:
        blockers.extend(production_validation.blockers);warnings.extend(production_validation.warnings);metrics.update({"production_validation":production_validation.passed})
    if traceability is not None:
        from photonx_eda_pcb.traceability_matrix.coverage import traceability_coverage
        cov=traceability_coverage(traceability);metrics["source_traceability"]=cov["source_coverage"];metrics["artifact_traceability"]=cov["artifact_coverage"]
        if cov["source_coverage"]<.95:blockers.append("MANUFACTURING_TRACEABILITY_SOURCE")
        if cov["artifact_coverage"]<.95:blockers.append("MANUFACTURING_TRACEABILITY_ARTIFACT")
    if fidelity is not None:
        metrics["roundtrip_fidelity"]=fidelity.score
        if fidelity.score<.95:blockers.append("MANUFACTURING_ROUNDTRIP_FIDELITY")
    return ManufacturingAudit(not blockers,sorted(set(blockers)),sorted(set(warnings)),metrics)
