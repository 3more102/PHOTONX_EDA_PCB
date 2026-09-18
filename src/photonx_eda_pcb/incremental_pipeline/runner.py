from .keys import make_stage_key
from .order import topological_order
from .model import StageState
def run_incremental(stages,handlers,cache,initial_keys=None,config=None):
    keys=dict(initial_keys or {});states=[];outputs={}
    for stage in topological_order(stages):
        deps=[keys[d] for d in stage.dependencies]
        key=make_stage_key(stage,deps,config)
        cached=cache.get(key,None)
        if cached is not None:value=cached;hit=True
        else:
            value=handlers[stage.name]([outputs.get(d) for d in stage.dependencies],config or {})
            cache.put(key,value);hit=False
        outputs[stage.name]=value;keys[stage.name]=key;states.append(StageState(stage.name,key,key,hit))
    return outputs,states
