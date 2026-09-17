def split_macro_statements(body):
    return [part.strip() for part in str(body).replace("\n","").split("*") if part.strip()]
