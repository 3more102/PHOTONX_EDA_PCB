from .model import GateFinding
def regression_findings(failures,thresholds):
    return [] if failures<=thresholds.max_regression_failures else [GateFinding('error','GATE_REGRESSION_FAILURES','regression failures exceed limit',failures,thresholds.max_regression_failures)]
