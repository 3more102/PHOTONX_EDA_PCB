INPUT_NAMES={"VIN","IN","INPUT","PVIN"}
OUTPUT_NAMES={"VOUT","OUT","OUTPUT","SW_OUT"}
ENABLE_NAMES={"EN","ENABLE","ON","SHDN","SHUTDOWN"}
FEEDBACK_NAMES={"FB","FEEDBACK","VSENSE","SENSE"}
GROUND_NAMES={"GND","PGND","AGND","VSS"}
def classify_pin_name(name):
    s=str(name or "").upper().replace(" ","")
    if s in INPUT_NAMES:return "input"
    if s in OUTPUT_NAMES:return "output"
    if s in ENABLE_NAMES:return "enable"
    if s in FEEDBACK_NAMES:return "feedback"
    if s in GROUND_NAMES:return "ground"
    return "unknown"
