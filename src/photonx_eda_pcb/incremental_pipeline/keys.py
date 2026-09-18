from photonx_eda_pcb.incremental_cache.key import stage_cache_key
def make_stage_key(stage,input_keys,config=None):
    return stage_cache_key(stage.name,{"dependencies":list(input_keys),"config":config or {}},stage.version)
