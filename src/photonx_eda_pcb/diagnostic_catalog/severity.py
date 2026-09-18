RANK={"info":0,"warning":1,"error":2,"critical":3}
def rank(severity):return RANK.get(str(severity).lower(),1)
