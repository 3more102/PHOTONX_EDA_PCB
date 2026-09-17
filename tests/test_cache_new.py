from photonx_eda_pcb.cache import MemoryCache,cache_key
def test_cache_and_key_determinism():
    assert cache_key("x",{"b":1,"a":2})==cache_key("x",{"a":2,"b":1})
    cache=MemoryCache(2); cache.put("a",1); cache.put("b",2); cache.put("c",3)
    assert cache.get("a") is None and cache.get("c")==3 and len(cache)==2
