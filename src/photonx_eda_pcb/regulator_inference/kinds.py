REGULATOR_TOKENS=("regulator","ldo","buck","boost","dc_dc","dcdc","converter","load_switch","pmic")
def regulator_kind(identity):
    text=" ".join(str(x or "") for x in (getattr(identity,"kind",None),getattr(identity,"value",None),getattr(identity,"mpn",None))).lower()
    if "ldo" in text:return "ldo"
    if "buck" in text:return "buck"
    if "boost" in text:return "boost"
    if "load_switch" in text or "load switch" in text:return "load_switch"
    if "pmic" in text:return "pmic"
    if "converter" in text or "dc_dc" in text or "dcdc" in text:return "converter"
    if "regulator" in text:return "regulator"
    return None
