def pin_roles(interface,labels):
    out={}
    for pin,net in interface.pins:
        out[pin]=str(labels.get(net,net))
    return out
