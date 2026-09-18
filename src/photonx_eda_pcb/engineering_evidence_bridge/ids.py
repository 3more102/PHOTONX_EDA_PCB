import hashlib
def evidence_id(kind,object_id,detail):
    raw=f"{kind}\0{object_id}\0{detail}".encode("utf-8")
    return "eng:"+hashlib.sha1(raw).hexdigest()[:16]
