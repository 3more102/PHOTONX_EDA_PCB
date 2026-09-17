def parse_polarity(text:str)->str:
    s=text.strip()
    if s=='%LPD*%': return 'dark'
    if s=='%LPC*%': return 'clear'
    raise ValueError('invalid polarity command')
