def numeric_strings(values=(-1,0,1,1e-9,1e9)):
    return [str(v) for v in values]

def malformed_records(prefix='X'):
    return ['',prefix,prefix+'*',prefix+'??',prefix+'999999999999999999']
