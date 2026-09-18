from .detect import detect_format
def detect_many(items):return [(path,detect_format(path,text)) for path,text in items]
