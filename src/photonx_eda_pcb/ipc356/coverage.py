def coverage(records,evidence):
    eligible=sum(1 for r in records if r.net_name and r.x is not None and r.y is not None)
    return 1.0 if eligible==0 else round(min(len(evidence)/eligible,1.0),12)
