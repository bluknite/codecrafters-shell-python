from app.command import Command
from app.command import find_command_path

class Type(Command):
    def __init__(self, args: list[str], out_file: str, err_file:str, append: bool):
        super().__init__(args, out_file, err_file, append)

    def invoke(self) -> bool:
        commmand = self.args[0]
        output = ""
        from app.built_ins.registry import registered_commands
        if commmand in registered_commands():
            output = f'{commmand} is a shell builtin\n'
        else:
            path = find_command_path(commmand)
            if path:
                output = f'{commmand} is {path}/{commmand}\n'
            else:
                output = f'{commmand}: not found\n'
        self.write_stdout(output, self.out_file, append=self.append)
        return True