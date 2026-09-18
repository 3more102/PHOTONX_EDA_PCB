from photonx_eda_pcb.analog_blocks.validation import validate_analog_block
def validate_analysis(a):
    issues=[]
    for b in a.blocks:issues.extend(validate_analog_block(b))
    ids=[x.id for x in a.evidence_records]
    if len(ids)!=len(set(ids)):issues.append("ANALOG_ANALYSIS_DUPLICATE_EVIDENCE")
    return issues
