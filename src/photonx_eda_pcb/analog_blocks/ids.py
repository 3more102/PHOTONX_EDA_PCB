import hashlib
def block_id(kind,components,nets):
    raw=str(kind)+"|"+",".join(sorted(map(str,components)))+"|"+",".join(sorted(map(str,nets)))
    return "analog:"+hashlib.sha1(raw.encode()).hexdigest()[:14]
