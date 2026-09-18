SIGNATURES={"I2C":{"SCL","SDA"},"SPI":{"SCLK","MOSI","MISO"},"UART":{"TX","RX"},"CAN":{"CANH","CANL"}}
def signal_role(label):
    s=str(label or "").upper().replace(" ","")
    for proto,roles in SIGNATURES.items():
        for r in roles:
            if r in s:return proto,r
    if "CS" in s or "NSS" in s:return "SPI","CS"
    return None
