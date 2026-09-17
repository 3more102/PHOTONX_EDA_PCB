from collections import Counter

def diff_summary(diff):
    c=Counter(x.kind for x in diff.entries)
    return {'total':len(diff.entries),'added':c['added'],'removed':c['removed'],'changed':c['changed']}
