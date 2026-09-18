def fpga_bank_report(items):
    return [{"component_id":x.component_id,"bank":x.bank,"supply_voltage":x.supply_voltage,"confidence":x.confidence,"pins":[p.__dict__ for p in x.pins]} for x in items]
