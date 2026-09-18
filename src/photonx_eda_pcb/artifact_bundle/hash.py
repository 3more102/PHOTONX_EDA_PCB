import hashlib
def content_hash(content):return hashlib.sha256(str(content).encode("utf-8")).hexdigest()
