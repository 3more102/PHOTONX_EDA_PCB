from .catalog import CATEGORIES
def validate_corpus(corpus):
    issues=[];ids=set()
    for c in corpus.cases:
        if c.id in ids:issues.append("CORPUS_DUPLICATE_ID")
        ids.add(c.id)
        if not c.inputs:issues.append("CORPUS_NO_INPUTS")
        if c.category not in CATEGORIES:issues.append("CORPUS_UNKNOWN_CATEGORY")
        if not c.expectation.metrics:issues.append("CORPUS_NO_EXPECTATIONS")
        if not c.synthetic and not c.description:issues.append("CORPUS_EXTERNAL_MISSING_DESCRIPTION")
        for v in c.expectation.tolerances.values():
            if float(v)<0:issues.append("CORPUS_NEGATIVE_TOLERANCE")
    return issues
