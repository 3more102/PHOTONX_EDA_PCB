from pathlib import Path
from .inventory import inventory
from .checksums import checksum_manifest
def build_manifest(root:str|Path)->dict[str,object]:
    root=Path(root); return {"root":root.name,"files":inventory(root),"sha256":checksum_manifest(root)}
