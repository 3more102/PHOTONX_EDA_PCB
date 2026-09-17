import hashlib
def sha256_bytes(data):return hashlib.sha256(data).hexdigest()
def sha256_text(text):return sha256_bytes(text.encode('utf-8'))
def valid_sha256(value):return isinstance(value,str) and len(value)==64 and all(c in '0123456789abcdef' for c in value.lower())
