def catalog_markdown(catalog):
    lines=["# Diagnostic Catalog","","| Code | Severity | Title |","|---|---|---|"]
    lines += [f"| {x.code} | {x.severity} | {x.title} |" for x in catalog.all()]
    return "\n".join(lines)+"\n"
