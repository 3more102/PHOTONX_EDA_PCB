import json
from .model import Command
def dump_command(c):return json.dumps({"name":c.name,"payload":c.payload,"source":c.source},sort_keys=True,separators=(",",":"))
def load_command(text):
    d=json.loads(text);return Command(str(d["name"]),dict(d.get("payload",{})),str(d.get("source","user")))
