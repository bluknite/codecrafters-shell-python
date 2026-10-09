from app.command import find_command
from app.completer import Completer
from app.debugger import Debugger
from app.shell_tokenizer import ShellTokenizer

import sys

def main():
    # Debugger.enable_debugging()
    Debugger.debug('\n\n\n\nNew Run')
    Debugger.debug('=======')
    Completer().register_hooks()
    while repl():
        pass

def repl():
    sys.stdout.write('$ ')
    command = input()
    return execute_command(command)

def execute_command(input: str) -> bool:
    Debugger.debug(f'\nReceived input: {input}')
    if input == "":
        return True
    args = ShellTokenizer.tokenize(input)
    if not args:
        print(f'Failed to parse input! {input}')
        return True

    command = args[0]

    # Handle redirection
    out_file = None
    err_file = None
    append = False
    if len(args) >= 3:
        if args[-2] == '>' or args[-2] == '1>' or args[-2] == '>>' or args[-2] == '1>>':
            out_file = args[-1]
            append = args[-2] == '>>' or args[-2] == '1>>'
            args = args[:-2]
        elif args[-2] == '2>' or args[-2] == '2>>':
            err_file = args[-1]
            append = args[-2] == '2>>'
            args = args[:-2]
    
    cmd = find_command(command)
    if cmd:
        return cmd.invoke(args[1:], out_file, err_file, append)
    print(f'{command}: command not found')
    return True

if __name__ == "__main__":
    main()
