from .coordinates import parse_coord
from .model import Ipc356Record
from .tokenize import key_values
def parse_record(line):
    raw=line.rstrip("\n"); stripped=raw.strip()
    if not stripped or stripped.startswith("C"): return None
    record_type=stripped[:3] if len(stripped)>=3 and stripped[:3].isdigit() else "UNKNOWN"
    fields=key_values(stripped)
    return Ipc356Record(record_type,fields.get("NET"),fields.get("REF") or fields.get("COMP"),fields.get("PIN"),parse_coord(fields.get("X")) if "X" in fields else None,parse_coord(fields.get("Y")) if "Y" in fields else None,fields.get("SIDE"),raw,fields)
def parse_ipc356(text): return [record for line in str(text).splitlines() if (record:=parse_record(line)) is not None]
