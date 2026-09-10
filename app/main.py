from pathlib import Path

import os
import readline
import subprocess
import sys

## Helpers for local debugging
debug_file = None

def set_debug_file(file_path):
    global debug_file
    debug_file = file_path

def debug(msg: str):
    if debug_file:
        debug_file_normalized = str.replace(debug_file, '~', os.environ.get('HOME'))
        with open(debug_file_normalized, 'a') as file:
            file.write(msg)
            file.write('\n')

def main():
    global debug_mode
    if debug_mode:
        set_debug_file('~/tmp/debug.out')
    debug('\nNew Run')
    debug('=======')
    readline.set_completer(invoke_completion)
    readline.set_completion_display_matches_hook(display_matches_hook)
    readline.parse_and_bind("tab: complete")
    readline.parse_and_bind("set bell-style audible")
    readline.parse_and_bind("set show-all-if-ambiguous off")
    while repl():
        pass

def repl():
    sys.stdout.write('$ ')
    command = input()
    return execute_command(command)

def execute_command(input: str) -> bool:
    debug(f'\nReceived input: {input}')
    if input == "":
        return True
    args = tokenize(input)
    if not args:
        print(f'Failed to parse input! {input}')
        return True
    command = args[0]
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
    

    if command in built_ins.keys():
        return built_ins[command](args[1:], out_file, err_file, append)
    path = find_command_path(command)
    if path:
        result = subprocess.run(
            args,
            cwd=path,
            capture_output=True,
            text=True
        )
        write_stdout(result.stdout, out_file, append=append)
        write_stderr(result.stderr, err_file, append=append)
        return True
    print(f'{command}: command not found')
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
    i = 0
    tokens = []

    while i < len(string):
        # if space advance to next non-space character
        while i < len(string) and string[i] == ' ':
            i += 1
        if i >= len(string):
            break
        if string[i] == "'":
            (i, token) = parse_single_quoted_string(string, i)
            if not i:
                return None
            tokens.append(token)
        elif string[i] == '"':
            (i, token) = parse_double_quoted_string(string, i)
            if not i:
                return None
            tokens.append(token)
        else:
            (i, token) = parse_unquoted_string(string, i)
            tokens.append(token)

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

def parse_unquoted_string(string: str, i:int) -> tuple[int, tuple[str, bool]]:
    if string[i] == '\\':
        i += 1
    j = i+1
    token = string[i]
    while j < len(string) and string[j] != ' ' and not is_quote(string[j]):
        if string[j] == '\\':
            j += 1
        token += string[j]
        j += 1
    return (j, (token, j < len(string) and is_quote(string[j])))

def parse_single_quoted_string(string: str, i: int) -> tuple[int, tuple[str, bool]]:
    j = i + 1
    token = ''
    while j < len(string) and string[j] != "'":
        token += string[j]
        j += 1
    
    if j >= len(string):
        print(f'Expected closing quote: {string[i:]}')
        return (None, None)
    return (j+1, (token, j < len(string) - 1 and string[j+1] != ' '))

def parse_double_quoted_string(string: str, i: int) -> tuple[int, tuple[str, bool]]:
    j = i + 1
    token = ''
    while j < len(string) and string[j] != '"':
        if string[j] == '\\':
            j += 1
        token += string[j]
        j += 1
    
    if j >= len(string):
        print(f'Expected closing quote: {string[i:]}')
        return (None, None)
    return (j+1, (token, j < len(string) - 1 and string[j+1] != ' '))

def is_quote(c: str) -> bool:
    return c == "'" or c == '"'

### Built-in commands ###
def cd(args: list[str], out_file: str, err_file: str, append: bool) -> bool:
    output = ""
    err = False
    if len(args) != 1:
        output = f'cd: expected 1 argument but found {len(args)}\n'
        err = True
    if args[0] == '~':
        os.chdir(os.environ.get('HOME'))
    elif os.path.isdir(args[0]):
        os.chdir(args[0])
    else:
        output = f'cd: {args[0]}: No such file or directory\n'
    if not err:
        write_stdout(output, out_file, append=append)
    else:
        write_stderr(output, err_file, append=append)
    return not err

def echo(args: list[str], out_file: str, err_file: str, append: bool) -> bool:
    output = ""
    for t in args:
        output += f'{t} '
    output += '\n'
    write_stdout(output, out_file, append=append)
    write_stderr('', err_file, append=append)
    return True

def exit(args: list[str], out_file: str, err_file: str, append: bool) -> bool:
    return False

def pwd(args: list[str], out_file: str, err_file: str, append: bool) -> bool:
    output = ""
    err = False
    if len(args) > 0:
        output = f'pwd: too many arguments\n'
        err = True
    else:
        output = f'{Path.cwd()}\n'
    if not err:
        write_stdout(output, out_file, append=append)
    else:
        write_stderr(output, err_file, append=append)
    return not err

def type(args: list[str], out_file: str, err_file: str, append: bool) -> bool:
    commmand = args[0]
    output = ""
    if commmand in built_ins.keys():
        output = f'{commmand} is a shell builtin\n'
    else:
        path = find_command_path(commmand)
        if path:
            output = f'{commmand} is {path}/{commmand}\n'
        else:
            output = f'{commmand}: not found\n'
    write_stdout(output, out_file, append=append)
    return True

def write_stdout(content: str, file: str, append = False):
    if file:
        write_to_file(content, file, append=append)
    else:
        sys.stdout.write(content)

def write_stderr(content: str, file: str, append = False):
    if file:
        write_to_file(content, file, append=append)
    else:
        sys.stderr.write(content)

def write_to_file(content: str, file_path: str, append=False):
    mode = 'a' if append else 'w'
    with open(file_path, mode) as file:
        file.write(content)

def invoke_completion(text: str, state: int) -> str:

    def find_matching_entries(commands: list[str]) -> list[str]:
        return [cmd for cmd in commands if cmd.startswith(text)]

    debug(f'Attempting to complete: {text} {state}')
    if len(text) == 0:
        return None
    COMMANDS = ['echo', 'exit']
    matches = find_matching_entries(COMMANDS)
    debug(f' Builtin match : {matches} {state}')
    try:
        debug('  RETURNING FROM BUILTIN')
        return f'{matches[state]} '
    except IndexError:
        if len(matches) > 0:
            return None
        debug('  NO BUILTIN MATCHES')

    debug('Looking for executable matches')
    all_matches = []
    for p in os.environ.get('PATH', '').split(os.pathsep):
        debug(f'  Checking path {p}')
        if os.path.isdir(p):
            with os.scandir(p) as entries:
                files = [entry.name for entry in entries if entry.is_file()]
                all_matches.extend(find_matching_entries(files))
                debug(f'    Total matches: {all_matches}')
    debug(f' Executable match : {all_matches} {state}')
    try:
        debug('  RETURNING FROM EXECUTABLE')
        return f'{all_matches[state]} '
    except IndexError:
        debug('  INDEX ERROR')
        pass

    return None

def display_matches_hook(substitution: str, matches: list, max_length: int):
    sys.stdout.write("\n")
    sys.stdout.write("  ".join(matches))
    sys.stdout.write(f'\n$ {substitution}')
    sys.stdout.flush()
    readline.redisplay()
        

built_ins = {
    'cd': cd,
    'echo': echo,
    'exit': exit,
    'pwd': pwd,
    'type': type
}

debug_mode = True

if __name__ == "__main__":
    main()
