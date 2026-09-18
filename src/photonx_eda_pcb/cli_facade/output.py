import json
def render_response(response,format="json"):
    if format=="json":
        return json.dumps({"success":response.success,"data":response.data,"error":response.error,"exit_code":response.exit_code},sort_keys=True,default=str)
    if response.success:return str(response.data)
    return response.error
