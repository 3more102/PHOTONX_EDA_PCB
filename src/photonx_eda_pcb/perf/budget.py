from dataclasses import dataclass
@dataclass(frozen=True)
class ResourceBudget:
    max_objects:int=5_000_000
    max_seconds:float|None=None
def check_object_budget(count,budget):
    if count>budget.max_objects: raise RuntimeError("object budget exceeded")
