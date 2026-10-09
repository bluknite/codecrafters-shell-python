from app.command import Command
from pathlib import Path

class Pwd(Command):
    def invoke(self, args: list[str], out_file: str, err_file: str, append: bool) -> bool:
        output = ""
        err = False
        if len(args) > 0:
            output = f'pwd: too many arguments\n'
            err = True
        else:
            output = f'{Path.cwd()}\n'
        if not err:
            self.write_stdout(output, out_file, append=append)
        else:
            self.write_stderr(output, err_file, append=append)
        return not err