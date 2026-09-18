def validate_container(container):
    return ["SERVICE_EMPTY_NAME"] if any(not str(n).strip() for n in container.names()) else []
