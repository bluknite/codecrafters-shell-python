from dataclasses import dataclass

from app.managed_process import ManagedProcess

import sys

class Backgrounder():
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.processes = []
    
    def register_job(self, pid, cmd, args, process) -> int:
        full_cmd = cmd + ' ' + ' '.join(args)
        jobid = 1 if len(self.processes) == 0 else max([job.jobid for job in self.processes]) + 1
        self.processes.append(Job(jobid, pid, full_cmd, process))
        return jobid

    def get_most_recent_job(self) -> str | None:
        if len(self.processes) == 0:
            return None
        job = self.processes[-1]
        state = 'Running' if job.process.is_running() else 'Done'
        return f'[{job.jobid}]+  {state:<24}{job.cmd}'

    def get_second_most_recent_job(self) -> str | None:
        if len(self.processes) < 2:
            return None
        job = self.processes[-2]
        state = 'Running' if job.process.is_running() else 'Done'
        return f'[{job.jobid}]-  {state:<24}{job.cmd}'

    def get_jobs(self) -> list[str] | None:
        job_strs = []
        for job in self.processes[:-2]:
            state = 'Running' if job.process.is_running() else 'Done'
            job_strs.append(f'[{job.jobid}]   {state:<24}{job.cmd}')
        job_strs.append(self.get_second_most_recent_job())
        job_strs.append(self.get_most_recent_job())
        result = [s for s in job_strs if s]
        self.refresh_jobs(print_done=False)
        if len(result) == 0:
            return None
        return result
    
    def refresh_jobs(self, print_done: bool):
        done_jobs = [job for job in self.processes if not job.is_running()]
        self.processes = [job for job in self.processes if job.is_running()]
        if print_done:
            for job in done_jobs:
                sys.stdout.write(f'[{job.jobid}]+  Done                    {job.cmd}\n')


@dataclass
class Job:
    jobid: int
    pid: int
    cmd: str
    process: ManagedProcess

    def is_running(self):
        return self.process.is_running()