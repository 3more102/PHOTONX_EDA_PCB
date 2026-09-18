def validate_command(command):
    issues=[]
    if not command.name.strip():issues.append("COMMAND_EMPTY_NAME")
    if not isinstance(command.payload,dict):issues.append("COMMAND_PAYLOAD_NOT_DICT")
    return issues
