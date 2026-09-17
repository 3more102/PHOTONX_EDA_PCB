def render_truth_report(result):
    return '# Ground truth comparison\n\n'+('PASS' if result.get('passed') else 'PARTIAL/FAIL')+'\n'
