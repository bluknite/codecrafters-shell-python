from app.command import Command

import os

class Cd(Command):
    def invoke(self, args: list[str], out_file: str, err_file: str, append: bool) -> bool:
        output = ""
        err = False
        if len(args) != 1:
            output = f'cd: expected 1 argument but found {len(args)}\n'
            err = True
        if args[0] == '~':
            os.chdir(os.environ.get('HOME'))
        elif os.path.isdir(args[0]):
            os.chdir(args[0])
        else:
            output = f'cd: {args[0]}: No such file or directory\n'
        if not err:
            self.write_stdout(output, out_file, append=append)
        else:
            self.write_stderr(output, err_file, append=append)
        return not err