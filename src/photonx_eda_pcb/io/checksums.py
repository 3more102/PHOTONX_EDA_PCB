from pathlib import Path
from ..core.hashing import sha256_file
def checksum_manifest(root:str|Path)->dict[str,str]:
    root=Path(root); return {p.relative_to(root).as_posix():sha256_file(p) for p in sorted(x for x in root.rglob("*") if x.is_file())}
