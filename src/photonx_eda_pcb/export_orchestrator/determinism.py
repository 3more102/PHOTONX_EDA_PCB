def stable_result_signature(results):
    return tuple((r.request_id,r.success,str(r.content),r.error) for r in sorted(results,key=lambda x:x.request_id))
