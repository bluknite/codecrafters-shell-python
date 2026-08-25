from pathlib import Path

import os
import subprocess
import sys


def main():
    while repl():
        pass

def repl():
    sys.stdout.write('$ ')
    command = input()
    return execute_command(command)

def execute_command(command: str) -> bool:
    args = command.split(' ')
    if args[0] in built_ins.keys():
        return built_ins[args[0]](args[1:])
    path = find_command_path(args[0])
    if path:
        subprocess.run(args, cwd=path)
        return True
    print(f'{command}: command not found')
    return True

def cd(args: list[str]) -> bool:
    if args[0] == '~':
        os.chdir(os.environ.get('HOME'))
    elif os.path.isdir(args[0]):
        os.chdir(args[0])
    else:
        print(f'cd: {args[0]}: No such file or directory')
    return True

def echo(args: list[[str]]) -> bool:
    for arg in args:
        sys.stdout.write(f'{arg} ')
    sys.stdout.write('\n')
    return True

def exit(args: list[str]) -> bool:
    return False

def pwd(args: list[str]) -> bool:
    current_dir = Path.cwd()
    print(current_dir)
    return True

def type(args: list[str]) -> bool:
    if args[0] in built_ins.keys():
        print(f'{args[0]} is a shell builtin')
        return True
    else:
        path = find_command_path(args[0])
        if path:
            print(f'{args[0]} is {path}/{args[0]}')
            return True
        print(f'{args[0]}: not found')
        return True

# find the path for the given command
def find_command_path(command: str) -> str | None:
    paths = os.environ.get('PATH', '').split(os.pathsep)
    for p in paths:
        file_path = f'{p}/{command}'
        if os.path.isfile(file_path) and os.access(file_path, os.X_OK):
            return p
    return None

built_ins = {
    'cd': cd,
    'echo': echo,
    'exit': exit,
    'pwd': pwd,
    'type': type
}

if __name__ == "__main__":
    main()
