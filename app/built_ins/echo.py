from app.command import Command

class Echo(Command):
    def __init__(self, args: list[str], out_file: str, err_file:str, append: bool):
        super().__init__(args, out_file, err_file, append)

    def invoke(self) -> bool:
        output = ""
        for t in self.args:
            output += f'{t} '
        output += '\n'
        self.write_stdout(output, self.out_file, append=self.append)
        self.write_stderr('', self.err_file, append=self.append)
        return True