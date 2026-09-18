import hashlib
def payload_hash(payload):return hashlib.sha256(str(payload).encode("utf-8")).hexdigest()
