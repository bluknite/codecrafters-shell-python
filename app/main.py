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

def execute_command(input: str) -> bool:
    args = tokenize(input)
    command = args[0]
    if command in built_ins.keys():
        return built_ins[command](args[1:])
    path = find_command_path(command)
    if path:
        subprocess.run(args, cwd=path)
        return True
    print(f'{command}: command not found')
    return True

def cd(args: list[str]) -> bool:
    if len(args) != 1:
        print(f'cd: expected 1 argument but found {len(args)}')
        return False
    if args[0] == '~':
        os.chdir(os.environ.get('HOME'))
    elif os.path.isdir(args[0]):
        os.chdir(args[0])
    else:
        print(f'cd: {args[0]}: No such file or directory')
    return True

def echo(args: list[str]) -> bool:
    for t in args:
        sys.stdout.write(f'{t} ')
    sys.stdout.write('\n')
    return True

def exit(args: list[str]) -> bool:
    return False

def pwd(args: list[str]) -> bool:
    if len(args) > 0:
        print(f'pwd: too many arguments')
        return False
    current_dir = Path.cwd()
    print(current_dir)
    return True

def type(args: list[str]) -> bool:
    commmand = args[0]
    if commmand in built_ins.keys():
        print(f'{commmand} is a shell builtin')
        return True
    else:
        path = find_command_path(commmand)
        if path:
            print(f'{commmand} is {path}/{commmand}')
            return True
        print(f'{commmand}: not found')
        return True

# find the path for the given command
def find_command_path(command: str) -> str | None:
    paths = os.environ.get('PATH', '').split(os.pathsep)
    for p in paths:
        file_path = f'{p}/{command}'
        if os.path.isfile(file_path) and os.access(file_path, os.X_OK):
            return p
    return None

def tokenize(string: str) -> list[str]:
    parts = string.strip().split(maxsplit=1)
    command = parts[0]
    result = [command]
    if len(parts) > 1:
        args = parts[1]
        args = args.replace("''", "")
        open_quote = args.find("'")
        while open_quote != -1:
            pre_quote = args[:open_quote]
            post_quote = args[open_quote+1:]
            pre_quote = pre_quote.strip()
            if len(pre_quote) > 0:
                result += pre_quote.split()
            close_quote = post_quote.find("'")
            result += [post_quote[:close_quote]]
            args = post_quote[close_quote+1:]
            open_quote = args.find("'")
        if len(args) > 0:
            result += args.strip().split()
    return result

built_ins = {
    'cd': cd,
    'echo': echo,
    'exit': exit,
    'pwd': pwd,
    'type': type
}

if __name__ == "__main__":
    main()

# echo this is 'a test' string here''there 'and everywhere'