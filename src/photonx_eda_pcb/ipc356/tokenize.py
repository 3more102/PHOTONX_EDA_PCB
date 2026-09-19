import re

_TOKEN = re.compile(r"([A-Z][A-Z0-9_]*)=([^\s]+)", re.IGNORECASE)


def key_values(line):
    fields = {}
    for match in _TOKEN.finditer(str(line)):
        key = match.group(1).upper()
        if key in fields:
            raise ValueError(f"duplicate IPC-356 field: {key}")
        fields[key] = match.group(2)
    return fields
