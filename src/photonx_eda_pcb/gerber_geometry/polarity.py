def apply_polarity(items,polarity='dark'):
    p=polarity.lower()
    if p not in {'dark','clear'}: raise ValueError('polarity must be dark or clear')
    return {'polarity':p,'items':list(items)}
