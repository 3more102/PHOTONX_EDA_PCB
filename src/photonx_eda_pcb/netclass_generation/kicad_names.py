def safe_class_name(name):
    out="".join(ch if ch.isalnum() or ch in "_-" else "_" for ch in str(name).strip())
    return out or "Generated"
