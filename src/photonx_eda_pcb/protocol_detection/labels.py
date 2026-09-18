def normalized_labels(labels):
    out={}
    for k,v in labels.items():
        s=str(v).upper().replace(" ","")
        s=s.replace("USB_D_P","D+").replace("USB_D_N","D-")
        s=s.replace("USB_DP","D+").replace("USB_DM","D-")
        s=s.replace("_P","+").replace("_N","-")
        s=s.replace("_","")
        out[str(k)]=s
    return out
