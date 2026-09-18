def label_function(label):
    s=str(label or "").upper().replace(" ","")
    exact={"GND":"ground","VSS":"ground","0V":"ground","SDA":"i2c_sda","SCL":"i2c_scl","MOSI":"spi_mosi","MISO":"spi_miso","SCLK":"spi_clock","TX":"uart_tx","RX":"uart_rx","CANH":"can_h","CANL":"can_l","D+":"usb_dp","D-":"usb_dm","USB_DP":"usb_dp","USB_DM":"usb_dm","RESET":"reset","RESET_N":"reset","SWDIO":"debug_swdio","SWCLK":"debug_swclk"}
    if s in exact:return exact[s]
    if any(x in s for x in ("VCC","VDD","+3V3","+5V","+12V","VBUS")):return "power"
    if "GPIO" in s:return "gpio"
    if "ADC" in s or "AIN" in s:return "analog_input"
    if "PWM" in s:return "pwm"
    return None
