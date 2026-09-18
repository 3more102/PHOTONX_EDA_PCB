from .metrics import detection_rate
def fault_report(results):return {"detection_rate":detection_rate(results),"results":[{"fault_id":x.fault_id,"detected":x.detected,"detector_output":str(x.detector_output)} for x in results]}
