import re
def safe_name(value):
    s=re.sub(r'[^A-Za-z0-9._-]+','_',str(value).strip());return s.strip('._') or 'artifact'
def artifact_filename(name,extension):
    ext=str(extension).lstrip('.');return f'{safe_name(name)}.{ext}' if ext else safe_name(name)
