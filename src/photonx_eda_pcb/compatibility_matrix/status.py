VALID_STATUS={"supported","partial","unsupported","experimental"}
RANK={"unsupported":0,"experimental":1,"partial":2,"supported":3}
def status_rank(s):return RANK[str(s)]
