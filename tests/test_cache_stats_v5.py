from photonx_eda_pcb.incremental_cache.store import IncrementalCache
from photonx_eda_pcb.incremental_cache.stats import cache_stats
def test_cache_stats():
    c=IncrementalCache();c.put("a",1);c.get("a");c.get("b")
    s=cache_stats(c)
    assert s["entries"]==1 and s["hit_rate"]==0.5
