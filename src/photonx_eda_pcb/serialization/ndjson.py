from .json_policy import dumps_strict, loads_strict


def encode_records(records):
    return "".join(
        dumps_strict(record, sort_keys=True) + "\n"
        for record in records
    )


def decode_records(text):
    return [
        loads_strict(line)
        for line in str(text).splitlines()
        if line.strip()
    ]
