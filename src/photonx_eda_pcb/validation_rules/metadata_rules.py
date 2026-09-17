from .base import RuleIssue
def metadata_sanity(board):
    m=getattr(board,'metadata',{}) or {}; out=[]
    if 'units' in m and m['units'] not in {'mm','inch'}: out.append(RuleIssue('warning','METADATA_UNITS','metadata units should be mm or inch'))
    if 'source_files' in m and not isinstance(m['source_files'],list): out.append(RuleIssue('warning','METADATA_SOURCE_FILES','source_files should be a list'))
    return out
