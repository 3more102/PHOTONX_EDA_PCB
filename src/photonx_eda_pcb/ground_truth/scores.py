def precision_recall(predicted:set,truth:set):
    tp=len(predicted & truth); p=tp/len(predicted) if predicted else (1.0 if not truth else 0.0); r=tp/len(truth) if truth else 1.0
    return {'precision':p,'recall':r,'f1':0.0 if p+r==0 else 2*p*r/(p+r)}
