import hashlib
from .manifest import dumps_corpus
def corpus_fingerprint(corpus):return hashlib.sha256(dumps_corpus(corpus).encode("utf-8")).hexdigest()
