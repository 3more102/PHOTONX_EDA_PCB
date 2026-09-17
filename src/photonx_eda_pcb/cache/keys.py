import hashlib,json
def cache_key(namespace,payload):
    raw=json.dumps(payload,sort_keys=True,separators=(",",":"),default=str)
    digest=hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"{namespace}:{digest}"
