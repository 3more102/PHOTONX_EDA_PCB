import hashlib,json
from .manifest import bundle_manifest
def bundle_signature(bundle):
    raw=json.dumps(bundle_manifest(bundle),sort_keys=True,separators=(",",":"))
    return hashlib.sha256(raw.encode()).hexdigest()
