from .statistics import duration_stats
from .scaling import percent_change
def compare_result(result,baseline_value):
    stats=duration_stats(result.durations);current=stats['median']
    return {'name':result.name,'ok':result.ok,'baseline':baseline_value,'current':current,'percent_change':None if current is None or baseline_value is None else percent_change(baseline_value,current)}
