def validate_change(c):
    return ["CHANGE_EMPTY_KEY"] if not str(c.key) else []
