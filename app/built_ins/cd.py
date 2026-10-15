from app.command import Command

import os

class Cd(Command):
    def __init__(self, args: list[str], out_file: str, err_file:str, append: bool):
        super().__init__(args, out_file, err_file, append)

    def invoke(self) -> bool:
        output = ""
        err = False
        if len(self.args) != 1:
            output = f'cd: expected 1 argument but found {len(self.args)}\n'
            err = True
        if self.args[0] == '~':
            os.chdir(os.environ.get('HOME'))
        elif os.path.isdir(self.args[0]):
            os.chdir(self.args[0])
        else:
            output = f'cd: {self.args[0]}: No such file or directory\n'
        if not err:
            self.write_stdout(output, self.out_file, append=self.append)
        else:
            self.write_stderr(output, self.err_file, append=self.append)
        return not err