from photonx_eda_pcb.evidence_database.model import EvidenceRecord
from .ids import evidence_id
def _record(object_id,kind,confidence,source,detail,group):
    return EvidenceRecord(evidence_id(kind,object_id,detail),str(object_id),str(kind),max(0.0,min(1.0,float(confidence))),str(source),str(detail),str(group))
def clock_records(items):
    return [_record(x.net_id,"clock_candidate",x.confidence,"clock_inference",",".join(x.evidence),"signal_role") for x in items]
def reset_records(items):
    return [_record(x.net_id,"reset_candidate",x.confidence,"reset_inference",f"active_low={x.active_low};"+",".join(x.evidence),"signal_role") for x in items]
def thermal_records(items):
    return [_record(x.object_id,"thermal_risk",x.confidence,"thermal_risk",f"risk={x.risk:.6f}","engineering_risk") for x in items]
def yield_records(item,object_id="board"):
    return [_record(object_id,"fabrication_yield_risk",.6,"fabrication_yield",f"score={item.score:.6f};level={item.level};drivers={','.join(item.drivers)}","engineering_risk")]
def pinmap_records(report):
    return [_record(report.component_id,"pinmap_issue",.9,"pinmap_reconciliation",f"{x.code}:{x.pin}:{x.expected}:{x.observed}","identity_validation") for x in report.issues]
