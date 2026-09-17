from .classification import classify_token

def reference_candidates(tokens):
    return {t.text:t for t in tokens if classify_token(t).startswith('reference_')}
