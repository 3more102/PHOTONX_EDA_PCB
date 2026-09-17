from .common import CommandResult
def capabilities_table(capabilities):
    rows=[]
    for item in capabilities: rows.append({'name':getattr(item,'name',str(item)),'status':getattr(item,'status','unknown')})
    return CommandResult(0,'capabilities listed',{'items':rows})
