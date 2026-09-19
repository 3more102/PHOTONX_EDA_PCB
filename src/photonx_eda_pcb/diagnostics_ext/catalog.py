from photonx_eda_pcb.diagnostic_catalog import default_catalog


_DEFAULT_CATALOG = default_catalog()
CATALOG = {
    definition.code: definition.description or definition.title
    for definition in _DEFAULT_CATALOG.all()
}


def definition_for(code):
    return _DEFAULT_CATALOG.get_optional(code)


def is_cataloged(code):
    return _DEFAULT_CATALOG.contains(code)


def uncataloged_codes(codes):
    return _DEFAULT_CATALOG.unknown_codes(codes)


def message_for(code):
    key = str(code)
    definition = definition_for(key)
    if definition is None:
        return f"Unknown diagnostic code: {key}."
    return definition.description or definition.title
