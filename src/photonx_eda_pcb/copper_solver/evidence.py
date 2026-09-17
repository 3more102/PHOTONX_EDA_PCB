def contact_confidence(geometry=True,same_layer=True,plating_proven=False,source_net=False):
    score=0.0
    if geometry:score+=0.45
    if same_layer:score+=0.25
    if plating_proven:score+=0.2
    if source_net:score+=0.1
    # Normalize binary floating-point accumulation so deterministic evidence
    # combinations produce stable confidence values across Python versions.
    return round(min(score,1.0),12)

def contact_reason(**flags):return ','.join(k for k,v in sorted(flags.items()) if v) or 'no_evidence'
