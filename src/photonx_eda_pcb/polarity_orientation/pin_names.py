POSITIVE_NAMES={"+","A","ANODE","POS","V+","VIN+"}
NEGATIVE_NAMES={"-","K","CATHODE","NEG","V-","GND"}
def polarity_from_pin_names(pins):
    pos=[];neg=[]
    for number,name in pins.items():
        n=str(name).upper()
        if n in POSITIVE_NAMES:pos.append(str(number))
        if n in NEGATIVE_NAMES:neg.append(str(number))
    return (pos[0] if len(pos)==1 else None,neg[0] if len(neg)==1 else None)
