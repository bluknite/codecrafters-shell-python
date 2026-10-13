from app.command import Command

class Jobs(Command):
    def invoke(self, args: list[str], out_file: str, err_file: str, append: bool) -> bool:
        return True