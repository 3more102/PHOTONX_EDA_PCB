import json
from .model import PackageEntry
from .catalog import PackageCatalog
def dumps_catalog(c):return json.dumps([e.__dict__ for e in c.all()],sort_keys=True,separators=(",",":"))
def loads_catalog(text):return PackageCatalog([PackageEntry(**x) for x in json.loads(text)])
