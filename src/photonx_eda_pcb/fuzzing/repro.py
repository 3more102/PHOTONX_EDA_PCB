import json

def reproduction_record(case,result):return json.dumps({'name':case.name,'payload':case.payload,'result':result},sort_keys=True)
