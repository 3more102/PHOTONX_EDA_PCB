import hashlib,json
from .canonical import canonical_schematic
def schematic_fingerprint(data):return hashlib.sha256(json.dumps(canonical_schematic(data),sort_keys=True,separators=(",",":")).encode()).hexdigest()
