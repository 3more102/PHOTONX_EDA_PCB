import json
from .model import Corpus,CorpusCase,CorpusExpectation
def dumps_corpus(corpus):
    data=[]
    for c in sorted(corpus.cases,key=lambda x:x.id):
        data.append({"id":c.id,"category":c.category,"inputs":list(c.inputs),"expectation":{"metrics":c.expectation.metrics,"tolerances":c.expectation.tolerances,"unknowns":list(c.expectation.unknowns)},"synthetic":c.synthetic,"description":c.description,"tags":list(c.tags)})
    return json.dumps({"cases":data},sort_keys=True,separators=(",",":"))
def loads_corpus(text):
    d=json.loads(text);cases=[]
    for x in d.get("cases",[]):
        ex=x["expectation"];cases.append(CorpusCase(str(x["id"]),str(x["category"]),tuple(map(str,x["inputs"])),CorpusExpectation(dict(ex["metrics"]),dict(ex.get("tolerances",{})),tuple(map(str,ex.get("unknowns",[])))),bool(x.get("synthetic",True)),str(x.get("description","")),tuple(map(str,x.get("tags",[])))))
    return Corpus(cases)
