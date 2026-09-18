OPS=(">=","<=","!=","==",">","<","~")
def parse_query(text):
    from .model import Query
    s=str(text).strip()
    for op in OPS:
        if op in s:
            field,value=s.split(op,1);field=field.strip();value=value.strip()
            if not field:raise ValueError("query field required")
            if value.lower() in {"true","false"}:v=value.lower()=="true"
            else:
                try:v=float(value) if "." in value else int(value)
                except ValueError:v=value.strip('"').strip("'")
            return Query(field,op,v)
    raise ValueError("query operator required")
