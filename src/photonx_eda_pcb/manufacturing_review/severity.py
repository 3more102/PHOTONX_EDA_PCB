RANK={"info":0,"warning":1,"error":2,"critical":3}
def severity_rank(name):return RANK.get(str(name).lower(),1)
