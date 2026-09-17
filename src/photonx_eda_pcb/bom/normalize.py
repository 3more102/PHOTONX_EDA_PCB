import re
def split_references(text): return tuple(part for part in re.split(r"[,;\s]+",str(text).strip()) if part)
def normalize_header(text): return str(text).strip().lower().replace(" ","_").replace("-","_")
