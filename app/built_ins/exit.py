from app.command import Command

class Exit(Command):
    def invoke(self, args: list[str], out_file: str, err_file: str, append: bool) -> bool:
        return False