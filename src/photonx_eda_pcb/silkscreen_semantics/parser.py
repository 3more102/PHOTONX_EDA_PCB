import re
from .tokens import SilkToken

def parse_silkscreen_text(text):
    words=re.findall(r'[A-Za-z0-9_+./-]+',text or '')
    return [SilkToken(w) for w in words]
