import re
def safe_label(value:str, fallback:str="unnamed")->str:
    s=re.sub(r"[^A-Za-z0-9_.+-]+","_",value.strip()).strip("_")
    return s or fallback
def truncate(value:str, limit:int=80)->str:
    if limit<1: raise ValueError("limit must be positive")
    return value if len(value)<=limit else value[:max(0,limit-1)]+"…"
