def parse_attribute_fields(text:str)->tuple[str,list[str]]:
    body=text.strip().strip('%').rstrip('*')
    if body.startswith(('TF.','TA.','TO.','TD')): body=body[2:] if body.startswith('TD') else body[3:]
    parts=[p.strip() for p in body.split(',')]
    return parts[0],parts[1:]
