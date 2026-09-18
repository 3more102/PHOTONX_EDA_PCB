import json
from .model import BatchJob
def load_batch_manifest(text):
    d=json.loads(text);return [BatchJob(str(x["id"]),str(x["command"]),tuple(map(str,x.get("inputs",[]))),dict(x.get("options",{}))) for x in d.get("jobs",[])]
def dump_batch_manifest(jobs):
    return json.dumps({"jobs":[{"id":j.id,"command":j.command,"inputs":list(j.inputs),"options":j.options} for j in jobs]},sort_keys=True,separators=(",",":"))
