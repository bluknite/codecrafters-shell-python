from app.built_ins.complete import Complete
from app.built_ins.pwd import Pwd
from app.command import Command
from app.built_ins.cd import Cd
from app.built_ins.echo import Echo
from app.built_ins.exit import Exit
from app.built_ins.type import Type

def registered_commands() -> list[str]:
    return list(built_ins.keys())

def find_builtin(command) -> Command | None:
    return built_ins.get(command)

built_ins = {
    'cd': Cd(),
    'complete': Complete(),
    'echo': Echo(),
    'exit': Exit(),
    'pwd': Pwd(),
    'type': Type()
}
