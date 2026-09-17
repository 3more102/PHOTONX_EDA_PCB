def match_external(reference,candidates):
    if not reference:return None
    key=reference.strip().upper()
    return next((x for x in candidates if str(x.get('reference','')).strip().upper()==key),None)
