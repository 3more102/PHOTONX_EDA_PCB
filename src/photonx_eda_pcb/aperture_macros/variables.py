def substitute(expr,variables):
    result=str(expr)
    for key,value in sorted(variables.items(),key=lambda item:-len(str(item[0]))):
        token=str(key) if str(key).startswith("$") else f"${key}"
        result=result.replace(token,str(value))
    return result
