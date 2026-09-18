import hashlib
def sha256_bytes(data):return hashlib.sha256(data).hexdigest()
def sha256_text(text):return sha256_bytes(str(text).encode("utf-8"))
