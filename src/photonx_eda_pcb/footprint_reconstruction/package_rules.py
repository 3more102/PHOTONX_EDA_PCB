def package_hint(features):
    n=features['count']; drilled=features['drilled']
    if n==2 and drilled==2:return 'TWO_PIN_THT'
    if n==2 and drilled==0:return 'TWO_PAD_SMD'
    if n==8 and drilled==8:return 'DIP8_LIKE'
    if n==8 and drilled==0:return 'SOIC8_LIKE'
    if n>=16 and drilled==0:return 'MULTIPIN_SMD'
    return None
