def no_crash_oracle(result):return result.get('status')=='ok'

def expected_exception_oracle(result,name):return result.get('exception')==name
