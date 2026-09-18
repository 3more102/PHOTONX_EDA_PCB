def parse_argv(argv):
    from .model import CliRequest
    args=list(argv)
    if not args:raise ValueError("command required")
    command=args.pop(0);pos=[];options={};i=0
    while i<len(args):
        token=args[i]
        if token.startswith("--"):
            key=token[2:]
            if not key:raise ValueError("empty option")
            if i+1<len(args) and not args[i+1].startswith("--"):options[key]=args[i+1];i+=2
            else:options[key]=True;i+=1
        else:pos.append(token);i+=1
    return CliRequest(command,tuple(pos),options)
