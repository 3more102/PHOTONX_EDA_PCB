import hashlib,json
def candidate_fingerprint(c):
    payload={"name":c.name,"commit":c.commit,"artifacts":[{"path":getattr(a,"path",getattr(a,"name","")),"sha256":getattr(a,"sha256",None)} for a in c.artifacts],"metadata":c.metadata}
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()
