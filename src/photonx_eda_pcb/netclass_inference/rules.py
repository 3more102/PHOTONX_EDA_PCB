POWER_TOKENS=("VCC","VDD","VBAT","+5V","+3V3","+12V","POWER")
GROUND_TOKENS=("GND","VSS","GROUND","0V")
HIGH_SPEED_TOKENS=("USB","PCIE","ETH","HDMI","MIPI","DDR","CLK")
def classify_features(f):
    label=f["label"];e=[]
    if any(t in label for t in GROUND_TOKENS):return "ground",0.95,("label_ground",)
    if any(t in label for t in POWER_TOKENS):return "power",0.9,("label_power",)
    if f["is_diff"]:return "differential",0.9,("pair_evidence",)
    if any(t in label for t in HIGH_SPEED_TOKENS):return "high_speed",0.75,("label_high_speed",)
    if f["max_width"] is not None and f["max_width"]>=0.8:return "power_candidate",0.55,("wide_trace",)
    return "signal",0.4,("default_physical",)
