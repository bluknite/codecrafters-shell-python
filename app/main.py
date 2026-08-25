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
    print(f'{command}: command not found')
    return True

def exit(args: list[str]) -> bool:
    return False

def echo(args: list[[str]]) -> bool:
    for arg in args:
        sys.stdout.write(f'{arg} ')
    sys.stdout.write('\n')
    return True

def type(args: list[str]) -> bool:
    if args[0] in built_ins.keys():
        print(f'{args[0]} is a shell builtin')
    else:
        print(f'{args[0]}: not found')
    return True

built_ins = {
    'echo': echo,
    'exit': exit,
    'type': type
}

if __name__ == "__main__":
    main()
