KNOWN_CAPABILITIES={"parser","exporter","validator","reporter","inference","gui_panel","cli_command"}
def validate_capabilities(items):
    return [x for x in items if x not in KNOWN_CAPABILITIES]
