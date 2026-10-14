from app.backgrounder import Backgrounder
from app.command import Command

class Jobs(Command):
    
    def invoke(self, args: list[str], out_file: str, err_file: str, append: bool) -> bool:
        job_strs = Backgrounder().get_jobs()
        if job_strs:
            for s in job_strs:
                self.write_stdout(f'{s}\n', out_file, append)
        return True