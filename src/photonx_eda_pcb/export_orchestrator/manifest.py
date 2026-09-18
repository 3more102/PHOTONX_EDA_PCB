import hashlib
def export_manifest(results):
    out=[]
    for r in results:
        data="" if r.content is None else str(r.content)
        out.append({"id":r.request_id,"success":r.success,"sha256":hashlib.sha256(data.encode()).hexdigest() if r.success else "","error":r.error})
    return out
