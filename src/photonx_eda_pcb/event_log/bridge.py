def log_command(bus_event_log,command,result=None):
    return bus_event_log.append("command",command.name,getattr(command,"source",""),data={"payload":command.payload,"result":result})
