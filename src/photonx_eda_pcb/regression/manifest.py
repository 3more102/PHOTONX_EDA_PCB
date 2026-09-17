import json
def load_cases(text):
    data=json.loads(text); return data.get('cases',[])
def dump_cases(cases): return json.dumps({'cases':cases},indent=2,sort_keys=True)+'\n'
