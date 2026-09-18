import json
def _obj(payload):
    try:return json.loads(payload)
    except Exception:return payload
def diff_snapshots(a,b):
    x,y=_obj(a.payload),_obj(b.payload)
    if isinstance(x,dict) and isinstance(y,dict):
        keys=sorted(set(x)|set(y));return {"changed":{k:(x.get(k),y.get(k)) for k in keys if x.get(k)!=y.get(k)}}
    return {"changed":None if x==y else (x,y)}
