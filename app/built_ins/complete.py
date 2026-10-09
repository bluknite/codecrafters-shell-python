from app.completer import Completer
from app.command import Command

class Complete(Command):
    def __init__(self):
        self.completer = Completer()

    def invoke(self, args: list[str], out_file: str, err_file: str, append: bool) -> bool:
        if len(args) >= 2:
            flag = args[0]
            if flag == '-C':
                self.completer.register_completer(args[2], args[1])
                return True
            elif flag == '-p':
                path = self.completer.get_completer_path(args[1])
                if path:
                    self.write_stdout(f"complete -C '{path}' {args[1]}\n", out_file, append=append)
                else:
                    self.write_stdout(f'complete: {args[1]}: no completion specification\n', out_file, append=append)
                return True
            else:
                self.write_stderr(f'complete: argument {args[0]} must be -p\n', err_file, append=append)
                return False
        return True