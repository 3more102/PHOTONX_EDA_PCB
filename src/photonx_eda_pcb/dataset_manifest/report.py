from .stats import dataset_stats
from .roles import role_counts
def dataset_report(m):return {"name":m.name,"version":m.version,"stats":dataset_stats(m),"roles":role_counts(m)}
