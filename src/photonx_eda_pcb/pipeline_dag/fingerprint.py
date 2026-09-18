import hashlib,json
def node_fingerprint(node,inputs,version="1"):
    payload={"name":node.name,"requires":list(node.requires),"produces":list(node.produces),"inputs":inputs,"version":str(version)}
    raw=json.dumps(payload,sort_keys=True,separators=(",",":"),default=str)
    return hashlib.sha256(raw.encode()).hexdigest()
