from .case import RegressionCase
def select_cases(cases,tags=()):
    tags=set(tags); return [c for c in cases if not tags or tags.intersection(c.tags)]
