def batch_job_to_cli(job):
    from .model import CliRequest
    return CliRequest(job.command,tuple(job.inputs),dict(job.options))
