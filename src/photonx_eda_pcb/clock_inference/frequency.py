def parse_frequency_hint(value):
    if value is None:return None
    s=str(value).strip().upper().replace(" ","")
    mult=1.0
    for suffix,m in (("GHZ",1e9),("MHZ",1e6),("KHZ",1e3),("HZ",1.0)):
        if s.endswith(suffix):
            mult=m;s=s[:-len(suffix)];break
    try:return float(s)*mult
    except ValueError:return None
