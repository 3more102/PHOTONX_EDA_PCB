import hashlib
def dataset_fingerprint(m):
    h=hashlib.sha256();h.update(f"{m.name}\0{m.version}\n".encode())
    for c in sorted(m.cases,key=lambda x:x.id):
        h.update(f"{c.id}\0{int(c.synthetic)}\0{c.license}\0{c.source}\n".encode())
        for f in sorted(c.files,key=lambda x:x.path):h.update(f"{f.path}\0{f.role}\0{f.sha256}\0{f.bytes}\n".encode())
    return h.hexdigest()
