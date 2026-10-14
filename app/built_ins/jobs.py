from app.backgrounder import Backgrounder
from app.command import Command

class Jobs(Command):
    
    def invoke(self, args: list[str], out_file: str, err_file: str, append: bool) -> bool:
        job_str = Backgrounder().get_most_recent_job()
        if job_str:
            self.write_stdout(f'{job_str}\n', out_file, append)
        return True