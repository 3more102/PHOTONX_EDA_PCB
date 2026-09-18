SUFFIX_PAIRS=(("_P","_N"),("+","-"),("_DP","_DM"))
def complementary_name(a,b):
    a=str(a);b=str(b)
    for p,n in SUFFIX_PAIRS:
        if a.endswith(p) and b==a[:-len(p)]+n:return True
        if b.endswith(p) and a==b[:-len(p)]+n:return True
    return False
