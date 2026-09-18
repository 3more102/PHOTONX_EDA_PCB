from photonx_eda_pcb.incremental_pipeline.planner import plan_recompute
from .model import InvalidationResult
def audit_invalidation(stages,expectation):
    planned=tuple(plan_recompute(stages,expectation.changed));exp=set(expectation.expected_recompute);got=set(planned)
    return InvalidationResult(exp==got,planned,tuple(sorted(exp-got)),tuple(sorted(got-exp)))
