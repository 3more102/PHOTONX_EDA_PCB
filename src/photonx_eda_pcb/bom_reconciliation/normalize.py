def normalize_text(value):return " ".join(str(value or "").strip().upper().split())
def normalize_reference(value):return normalize_text(value).replace(" ","")
