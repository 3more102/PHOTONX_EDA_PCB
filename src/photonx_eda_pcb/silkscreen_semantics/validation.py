def validate_token(token):
    issues=[]
    if not token.text.strip():issues.append('SILK_TEXT_EMPTY')
    if token.layer not in {'F.SilkS','B.SilkS'}:issues.append('SILK_LAYER_UNKNOWN')
    return issues
