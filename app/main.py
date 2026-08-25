import sys


def main():
    while repl():
        pass

def repl():
    sys.stdout.write('$ ')
    command = input()
    return execute_command(command)

def execute_command(command: str) -> bool:
    if command == 'exit':
        return False
    elif command.startswith('echo'):
        return echo(command)
    print(f'{command}: command not found')
    return True

def echo(command: str) -> bool:
    print(command[5:])
    return True

if __name__ == "__main__":
    main()
