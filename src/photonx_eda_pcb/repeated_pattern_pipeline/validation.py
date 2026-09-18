from photonx_eda_pcb.subgraph_fingerprints.validation import validate_fingerprint
from photonx_eda_pcb.repeated_circuits.validation import validate_group
from photonx_eda_pcb.channel_detection.validation import validate_channel
def validate_analysis(a):
    issues=[]
    for x in a.fingerprints:issues.extend(validate_fingerprint(x))
    for x in a.repeated_groups:issues.extend(validate_group(x))
    for x in a.channels:issues.extend(validate_channel(x))
    ids=[x.id for x in a.evidence_records]
    if len(ids)!=len(set(ids)):issues.append("REPEATED_ANALYSIS_DUPLICATE_EVIDENCE")
    return issues
