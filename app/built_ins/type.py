from app.command import Command
from app.command import find_command_path

class Type(Command):
    def invoke(self, args: list[str], out_file: str, err_file: str, append: bool) -> bool:
        commmand = args[0]
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
        self.write_stdout(output, out_file, append=append)
        return True