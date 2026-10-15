from app.backgrounder import Backgrounder
from app.command import parse_command
from app.completer import Completer
from app.debugger import Debugger

import sys

def main():
    # Debugger.enable_debugging()
    Debugger.debug('\n\n\n\nNew Run')
    Debugger.debug('=======')
    Completer().register_hooks()
    while repl():
        pass

def repl():
    Backgrounder().refresh_jobs(print_done=True)
    sys.stdout.write('$ ')
    command = input()
    return execute_command(command)

def execute_command(input: str) -> bool:
    (cmd, command) = parse_command(input)
    if cmd:
        return cmd.invoke()
    if command:
        print(f'{command}: command not found')
    return True

if __name__ == "__main__":
    main()
