def results_markdown(results):
    lines=["# Batch Results","","| Job | Success | Error |","|---|---|---|"]
    lines += [f"| {r.job_id} | {'yes' if r.success else 'no'} | {r.error.replace('|','/')} |" for r in results]
    return "\n".join(lines)+"\n"
