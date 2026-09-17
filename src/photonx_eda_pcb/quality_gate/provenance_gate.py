from .model import GateFinding
def provenance_findings(coverage,thresholds):
    return [] if coverage>=thresholds.min_provenance_coverage else [GateFinding('error','GATE_PROVENANCE_LOW','provenance coverage below threshold',coverage,thresholds.min_provenance_coverage)]
