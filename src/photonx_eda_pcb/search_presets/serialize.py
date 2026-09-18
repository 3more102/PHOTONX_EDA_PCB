import json
from .model import SearchPreset
from .store import PresetStore
def dumps_presets(store):return json.dumps([p.__dict__ for p in store.all()],sort_keys=True,separators=(",",":"))
def loads_presets(text):return PresetStore.from_list([SearchPreset(**x) for x in json.loads(text)]) if hasattr(PresetStore,"from_list") else _load(text)
def _load(text):
    s=PresetStore()
    for x in json.loads(text):s.add(SearchPreset(**x))
    return s
