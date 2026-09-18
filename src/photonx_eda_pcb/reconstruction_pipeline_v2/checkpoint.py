import json
def checkpoint_payload(context):
    return json.dumps({"artifacts":sorted(context.artifacts),"diagnostics":list(context.diagnostics),"metrics":context.metrics},sort_keys=True,separators=(",",":"))
