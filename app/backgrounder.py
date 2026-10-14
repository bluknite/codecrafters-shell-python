from dataclasses import dataclass
class Backgrounder():
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.nextid = 1
            self.processes = []
    
    def register_job(self, pid, cmd, args) -> int:
        full_cmd = cmd + ' ' + ' '.join(args)
        self.processes.append(Job(self.nextid, pid, full_cmd))
        # self.processes[self.nextid] = (pid, full_cmd)
        self.nextid += 1
        return self.nextid - 1
    
    def get_most_recent_job(self) -> str | None:
        if len(self.processes) == 0:
            return None
        job = self.processes[-1]
        return f'[{job.jobid}]+  Running                 {job.cmd}'


@dataclass
class Job:
    jobid: int
    pid: int
    cmd: str