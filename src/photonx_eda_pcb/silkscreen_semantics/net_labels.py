from .classification import classify_token

def net_label_candidates(tokens):return [t.text for t in tokens if classify_token(t)=='net_label_candidate']
