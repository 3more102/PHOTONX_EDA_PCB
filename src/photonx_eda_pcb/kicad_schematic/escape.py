def kicad_string(value):
    s=str(value).replace("\\","\\\\").replace('"','\\"').replace("\n"," ")
    return f'"{s}"'
