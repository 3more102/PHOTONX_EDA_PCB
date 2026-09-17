def header(text): return str(text).strip().lower().replace(" ","_").replace("-","_")
def side(text):
    value=str(text or "top").strip().lower()
    return "bottom" if value in {"bottom","bot","b","back"} else "top"
