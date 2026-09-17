import hashlib
def content_sha256(text): return hashlib.sha256(str(text).encode("utf-8")).hexdigest()
