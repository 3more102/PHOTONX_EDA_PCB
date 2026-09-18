import hashlib
def stable_digest(payload):return hashlib.sha256(str(payload).encode("utf-8")).hexdigest()
