import hashlib,json
def manifest_signature(m):
    payload={"version":m.version,"commit":m.commit,"artifacts":[a.__dict__ for a in m.artifacts],"metadata":m.metadata}
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
