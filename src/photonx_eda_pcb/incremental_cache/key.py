import hashlib,json
def stage_cache_key(stage,inputs,version="1"):
    payload=json.dumps({"stage":str(stage),"inputs":inputs,"version":str(version)},sort_keys=True,separators=(",",":"),default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
