def intent_summary(power,ground,decoupling,connectors):
    return {"power_nets":list(power),"ground_nets":list(ground),"decoupling":list(decoupling),"connectors":list(connectors)}
