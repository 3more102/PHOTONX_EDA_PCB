import hashlib
def workspace_fingerprint(index):
    h=hashlib.sha256()
    for a in sorted(index.artifacts,key=lambda x:x.path):
        h.update(f"{a.path}\0{a.role}\0{a.size}\0{a.sha256}\n".encode())
    return h.hexdigest()
