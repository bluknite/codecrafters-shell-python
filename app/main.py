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
    if input == "":
        return True
    args = tokenize(input)
    if not args:
        print(f'Failed to parse input! {input}')
        return True
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
        parsed_args = parse_args(parts[1])
        if not parsed_args:
            print(f'Error parsing arguments: {parts[1]}')
            return None
        result += parsed_args
    return result

def parse_args(string: str) -> list[str]:
    i = 0
    tokens = []

    def handle_quoted_string(quote_type: str, i: int) -> int:
        j = i + 1
        token = ''
        while j < len(string) and string[j] != quote_type:
            if string[j] == '\\':
                j += 1
            token += string[j]
            j += 1
        
        if j >= len(string):
            print(f'Expected closing quote: {string[i:]}')
            return None
        tokens.append((token, j < len(string) - 1 and string[j+1] != ' '))
        return j+1

    while i < len(string):
        # if space advance to next non-space character
        while string[i] == ' ':
            i += 1
        # if single-quote, find next single-quote
        if string[i] == "'":
            i = handle_quoted_string("'", i)
            if not i:
                return None
        # if double-quote, find next double-quote
        elif string[i] == '"':
            i = handle_quoted_string('"', i)
            if not i:
                return None
        # if non-quote, find next space or quote
        else:
            if string[i] == '\\':
                i += 1
            j = i+1
            token = string[i]
            while j < len(string) and string[j] != ' ' and not is_quote(string[j]):
                if string[j] == '\\':
                    j += 1
                token += string[j]
                j += 1
            tokens.append((token, j < len(string) and is_quote(string[j])))
            i = j

    merged = True
    while merged:
        merged = False
        new_tokens = []
        i = 0
        while i < len(tokens):
            t = tokens[i]
            if not t[1]:
                new_tokens.append(t)
                i += 1
            else:
                t2 = tokens[i+1]
                new_tokens.append((t[0] + t2[0], t2[1]))
                merged = True
                i += 2
        tokens = new_tokens

    return [t[0] for t in tokens]

def is_quote(c: str) -> bool:
    return c == "'" or c == '"'

built_ins = {
    'cd': cd,
    'echo': echo,
    'exit': exit,
    'pwd': pwd,
    'type': type
}

if __name__ == "__main__":
    main()
