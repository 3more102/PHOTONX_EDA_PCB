from collections import Counter

def fuzz_statistics(results):
    c=Counter(x['status'] for x in results)
    return {'total':len(results),'ok':c['ok'],'exceptions':c['exception']}
