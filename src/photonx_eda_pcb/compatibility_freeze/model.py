from dataclasses import dataclass
@dataclass(frozen=True)
class CompatibilityFreezeDecision:
    passed:bool
    blockers:tuple[str,...]
    warnings:tuple[str,...]
    feature_count:int
    migration_count:int
