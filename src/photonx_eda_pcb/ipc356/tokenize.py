import re
_TOKEN=re.compile(r"([A-Z][A-Z0-9_]*)=([^\s]+)")
def key_values(line): return {key:value for key,value in _TOKEN.findall(line.upper())}
