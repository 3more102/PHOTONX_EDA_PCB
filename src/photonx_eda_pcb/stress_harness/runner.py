from time import perf_counter
def run_stress_case(case,fn,*args,**kwargs):
    samples=[];last=None
    for _ in range(max(1,int(case.repetitions))):
        t=perf_counter();last=fn(*args,**kwargs);samples.append(perf_counter()-t)
    return {"name":case.name,"size":case.size,"samples":samples,"min_s":min(samples),"max_s":max(samples),"mean_s":sum(samples)/len(samples),"result":last}
