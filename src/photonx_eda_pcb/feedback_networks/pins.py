FEEDBACK_NAMES={"FB","FEEDBACK","INV","IN-","-","VFB"}
def feedback_pins(pin_names):
    return tuple(sorted(str(pin) for pin,name in pin_names.items() if str(name).upper().replace(" ","") in FEEDBACK_NAMES))
