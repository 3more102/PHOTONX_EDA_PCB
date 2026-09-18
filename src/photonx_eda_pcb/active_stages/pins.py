POS={"IN+","NONINV","+","PLUS"};NEG={"IN-","INV","-","MINUS"};OUT={"OUT","OUTPUT","Y"}
def active_pin_roles(pin_names):
    roles={}
    for pin,name in pin_names.items():
        n=str(name).upper().replace(" ","")
        if n in POS:roles["noninverting"]=str(pin)
        elif n in NEG:roles["inverting"]=str(pin)
        elif n in OUT:roles["output"]=str(pin)
    return roles
