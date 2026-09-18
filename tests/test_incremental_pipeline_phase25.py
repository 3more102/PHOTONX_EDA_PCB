from photonx_eda_pcb.incremental_pipeline import StageSpec,run_incremental
from photonx_eda_pcb.incremental_cache.store import IncrementalCache
def test_incremental_pipeline_uses_cache():
    stages=[StageSpec("parse"),StageSpec("geometry",("parse",))]
    calls={"parse":0,"geometry":0}
    handlers={"parse":lambda deps,cfg:(calls.__setitem__("parse",calls["parse"]+1) or "p"),"geometry":lambda deps,cfg:(calls.__setitem__("geometry",calls["geometry"]+1) or deps[0]+"g")}
    cache=IncrementalCache()
    out,s1=run_incremental(stages,handlers,cache);out2,s2=run_incremental(stages,handlers,cache)
    assert out["geometry"]=="pg" and out2==out
    assert calls=={"parse":1,"geometry":1} and all(x.cached for x in s2)
