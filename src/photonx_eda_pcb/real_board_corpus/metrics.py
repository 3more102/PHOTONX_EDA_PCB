def compare_metrics(expected,actual,tolerances=None):
    tolerances=tolerances or {};out={}
    for k,v in expected.items():
        a=actual.get(k)
        if a is None:out[k]={"status":"missing","expected":v,"actual":None};continue
        tol=float(tolerances.get(k,0))
        ok=abs(float(a)-float(v))<=tol
        out[k]={"status":"pass" if ok else "fail","expected":v,"actual":a,"tolerance":tol}
    return out
