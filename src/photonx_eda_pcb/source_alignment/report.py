def alignment_report(transform,rms):
    return {"dx":transform.dx,"dy":transform.dy,"scale":transform.scale,"rotation_deg":transform.rotation_deg,"rms_error":rms}
