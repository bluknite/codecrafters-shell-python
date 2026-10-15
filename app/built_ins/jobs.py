from app.backgrounder import Backgrounder
from app.command import Command

class Jobs(Command):
    def __init__(self, args: list[str], out_file: str, err_file:str, append: bool):
        super().__init__(args, out_file, err_file, append)

    def invoke(self) -> bool:
        job_strs = Backgrounder().get_jobs()
        if job_strs:
            for s in job_strs:
                self.write_stdout(f'{s}\n', self.out_file, append=self.append)
        return True