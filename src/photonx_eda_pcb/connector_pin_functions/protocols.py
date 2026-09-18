PROTOCOL_ROLE_MAP={"I2C":{"SDA":"i2c_sda","SCL":"i2c_scl"},"SPI":{"MOSI":"spi_mosi","MISO":"spi_miso","SCLK":"spi_clock","CS":"spi_cs"},"UART":{"TX":"uart_tx","RX":"uart_rx"},"CAN":{"CANH":"can_h","CANL":"can_l"}}
def protocol_function(protocol,label):
    p=str(protocol).upper();s=str(label or "").upper()
    for token,fn in PROTOCOL_ROLE_MAP.get(p,{}).items():
        if token in s:return fn
    if p=="USB":
        if "D+" in s or "DP" in s:return "usb_dp"
        if "D-" in s or "DM" in s:return "usb_dm"
    return None
