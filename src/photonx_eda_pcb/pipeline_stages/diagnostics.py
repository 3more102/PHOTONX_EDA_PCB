from collections import Counter
def pipeline_diagnostic_counts(ctx):return dict(Counter(x.get('code','UNKNOWN') for x in ctx.diagnostics if isinstance(x,dict)))
def failed_stages(results):return [getattr(r,'name',r[0] if isinstance(r,tuple) else '?') for r in results if (hasattr(r,'ok') and not r.ok) or (isinstance(r,tuple) and len(r)>1 and r[1] is False)]
