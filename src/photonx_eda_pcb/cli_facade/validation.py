def validate_request(request):
    issues=[]
    if not request.command.strip():issues.append("CLI_EMPTY_COMMAND")
    if not isinstance(request.options,dict):issues.append("CLI_OPTIONS_NOT_DICT")
    return issues
