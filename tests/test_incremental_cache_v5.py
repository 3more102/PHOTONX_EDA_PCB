from photonx_eda_pcb.incremental_cache import stage_cache_key,IncrementalCache,DependencyIndex
from photonx_eda_pcb.incremental_cache.invalidation import invalidate_tree
def test_incremental_cache_and_dependency_invalidation():
    c=IncrementalCache();idx=DependencyIndex()
    a=stage_cache_key("parse",{"sha":"x"});b=stage_cache_key("geom",{"parent":a})
    c.put(a,1);c.put(b,2);idx.add(a,b)
    assert c.get(a)==1
    removed=invalidate_tree(c,idx,a)
    assert set(removed)=={a,b} and len(c)==0
