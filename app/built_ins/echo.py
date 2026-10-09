from app.command import Command

class Echo(Command):
    def invoke(self, args: list[str], out_file: str, err_file: str, append: bool) -> bool:
        output = ""
        for t in args:
            output += f'{t} '
        output += '\n'
        self.write_stdout(output, out_file, append=append)
        self.write_stderr('', err_file, append=append)
        return True