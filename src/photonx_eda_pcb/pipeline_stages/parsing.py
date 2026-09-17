from .stage import StageResult
def parsing_stage(ctx):
    parser=ctx.inputs.get('parser')
    if parser is None:return StageResult('parsing',False,diagnostics=({'severity':'error','code':'PARSER_MISSING'},))
    parsed=[parser(x) for x in ctx.get('discovered_files',[])];ctx.put('parsed_inputs',parsed)
    return StageResult('parsing',True,('parsed_inputs',),metadata={'count':len(parsed)})
