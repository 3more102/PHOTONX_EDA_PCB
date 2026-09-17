import platform,sys
def environment_info():return {'python':platform.python_version(),'implementation':platform.python_implementation(),'platform':platform.platform(),'machine':platform.machine(),'executable':sys.executable}
