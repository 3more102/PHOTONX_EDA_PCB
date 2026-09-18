def validate_fpga_bank(bank):
    issues=[]
    if not bank.bank:issues.append("FPGA_BANK_EMPTY")
    if not 0<=bank.confidence<=1:issues.append("FPGA_BANK_CONFIDENCE_RANGE")
    pins=[x.pin for x in bank.pins]
    if len(pins)!=len(set(pins)):issues.append("FPGA_BANK_DUPLICATE_PIN")
    return issues
