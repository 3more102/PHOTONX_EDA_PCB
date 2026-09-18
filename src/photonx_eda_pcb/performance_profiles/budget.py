from dataclasses import dataclass
@dataclass(frozen=True)
class PerformanceBudget:
    name:str
    max_seconds:float
    max_regression_ratio:float=1.25
def budget_passed(result,budget):return result.median_seconds<=budget.max_seconds
def regression_passed(before,after,budget):
    return before.median_seconds<=0 or after.median_seconds/before.median_seconds<=budget.max_regression_ratio
