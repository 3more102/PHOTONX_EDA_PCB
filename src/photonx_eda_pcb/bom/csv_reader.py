import csv,io
from .model import BomItem
from .normalize import normalize_header,split_references
def read_bom_csv(text):
    reader=csv.DictReader(io.StringIO(str(text)))
    result=[]
    for row in reader:
        normalized={normalize_header(key):value for key,value in row.items() if key is not None}
        refs=normalized.get("references") or normalized.get("reference") or normalized.get("designators") or ""
        qty=normalized.get("quantity") or normalized.get("qty")
        result.append(BomItem(split_references(refs),normalized.get("value","") or "",normalized.get("footprint","") or "",normalized.get("mpn","") or normalized.get("part_number","") or "",normalized.get("manufacturer","") or "",int(qty) if str(qty or "").isdigit() else None))
    return result
