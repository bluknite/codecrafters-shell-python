from app.completer import Completer
from app.command import Command

class Complete(Command):
    def __init__(self, args: list[str], out_file: str, err_file:str, append: bool):
        super().__init__(args, out_file, err_file, append)
        self.completer = Completer()

    def invoke(self) -> bool:
        if len(self.args) >= 2:
            flag = self.args[0]
            if flag == '-C':
                self.completer.register_completer(self.args[2], self.args[1])
                return True
            elif flag == '-p':
                path = self.completer.get_completer_path(self.args[1])
                if path:
                    self.write_stdout(f"complete -C '{path}' {self.args[1]}\n", self.out_file, append=self.append)
                else:
                    self.write_stdout(f'complete: {self.args[1]}: no completion specification\n', self.out_file, append=self.append)
                return True
            elif flag == '-r':
                self.completer.unregister_completer(self.args[1])
            else:
                self.write_stderr(f'complete: argument {self.args[0]} must be -C or -p\n', self.err_file, append=self.append)
                return False
        return True