from app.command import Command
from pathlib import Path

class Pwd(Command):
    def __init__(self, args: list[str], out_file: str, err_file:str, append: bool):
        super().__init__(args, out_file, err_file, append)

    def invoke(self) -> bool:
        output = ""
        err = False
        if len(self.args) > 0:
            output = f'pwd: too many arguments\n'
            err = True
        else:
            output = f'{Path.cwd()}\n'
        if not err:
            self.write_stdout(output, self.out_file, append=self.append)
        else:
            self.write_stderr(output, self.err_file, append=self.append)
        return not err