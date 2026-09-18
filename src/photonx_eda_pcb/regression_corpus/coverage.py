def corpus_coverage(corpus):
    cats={c.category for c in corpus.cases}
    synthetic=sum(c.synthetic for c in corpus.cases)
    return {"cases":len(corpus.cases),"categories":len(cats),"synthetic":synthetic,"external":len(corpus.cases)-synthetic}
