def split_macro_statements(body):
    normalized = (
        str(body)
        .replace("\r\n", " ")
        .replace("\r", " ")
        .replace("\n", " ")
    )
    return [part.strip() for part in normalized.split("*") if part.strip()]
