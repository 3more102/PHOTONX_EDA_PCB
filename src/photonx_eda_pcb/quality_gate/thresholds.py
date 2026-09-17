from dataclasses import dataclass
@dataclass(frozen=True)
class QualityThresholds:
    max_errors:int=0;max_warnings:int=100;min_provenance_coverage:float=0.5;min_completeness:float=0.5;max_regression_failures:int=0
