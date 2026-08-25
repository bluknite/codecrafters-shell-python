import sys


def main():
    while repl():
        pass

def repl():
    sys.stdout.write('$ ')
    command = input()
    if command == 'exit':
        return False
    sys.stdout.write(f'{command}: command not found\n')
    return True

if __name__ == "__main__":
    main()
