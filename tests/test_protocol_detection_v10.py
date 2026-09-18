from photonx_eda_pcb.protocol_detection import detect_protocols,validate_candidates
def test_detect_i2c_and_usb_aliases():
    r=detect_protocols({"n1":"I2C_SCL","n2":"I2C_SDA","n3":"USB_D_P","n4":"USB_D_N"})
    names={x.protocol for x in r}
    assert "i2c" in names and "usb" in names
    assert validate_candidates(r)==[]
