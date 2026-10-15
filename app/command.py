from abc import ABC, abstractmethod
from app.backgrounder import Backgrounder
from app.debugger import Debugger
from app.managed_process import ManagedProcess
from app.shell_tokenizer import ShellTokenizer

import os
import subprocess
import sys

class Command(ABC):
    def __init__(self, args: list[str], out_file: str, err_file:str, append: bool):
        self.args = args
        self.out_file = out_file
        self.err_file = err_file
        self.append = append

    @abstractmethod
    def invoke(self) -> bool:
        """
        Invokes the command with the given arguments.

        Params:
            args: List of arguments to the command
            out_file: File to redirect standard output to
            err_file: File to redirect standard error to
            append: Whether to append to the output files

        Returns:
            True if the command was executed successfully, False if the command should cause a shell exit.
        """
        pass

    def write_stdout(self, content: str, file: str, append = False):
        """
        Writes the given content to standard output or the file provided.
        
        Params:
            content: Content to write to standard output
            file: File to write to
            append: Whether to append to the file
        """
        self.write_stdout_func(file, append)(content)

    def write_stderr(self, content: str, file: str, append = False):
        """
        Writes the given content to standard error or the file provided.
        
        Params:
            content: Content to write to standard error
            file: File to write to
            append: Whether to append to the file
        """
        self.write_stderr_func(file, append)(content)
    
    def write_stdout_func(self, file: str, append: bool) -> callable:
        def func(content: str):
            if file:
                self.write_to_file(content, file, append=append)
            else:
                sys.stdout.write(content)
        return func
    
    def write_stderr_func(self, file: str, append: bool) -> callable:
        def func(content: str):
            if file:
                self.write_to_file(content, file, append=append)
            else:
                sys.stderr.write(content)
        return func

    def write_to_file(self, content: str, file_path: str, append=False):
        """
        Writes the given content to the file provided.
        
        Params:
            content: Content to write to the file
            file_path: File to write to
            append: Whether to append to the file
        """
        mode = 'a' if append else 'w'
        with open(file_path, mode) as file:
            file.write(content)

def parse_command(input: str) -> tuple[Command | None, str | None]:
    Debugger.debug(f'\nReceived input: {input}')
    if input == "":
        return (None, None)
    args = ShellTokenizer.tokenize(input)
    if not args:
        print(f'Failed to parse input! {input}')
        return (None, None)

    command = args[0]

    # Check for background process
    background = False
    if args[-1] == '&':
        background = True
        args = args[:-1]

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
    
    cmd = find_command(command, background, args[1:], out_file, err_file, append)
    return (cmd, command)

def find_command(command: str, background: bool, args: list[str], out_file: str, err_file:str, append: bool) -> Command | None:
    from app.built_ins.registry import find_builtin
    c = find_builtin(command)
    if c:
        return c(args, out_file, err_file, append=append)
    path = find_command_path(command)
    if path:
        if background:
            return BackgroundPathCommand(path, command, args, out_file, err_file, append)
        return PathCommand(path, command, args, out_file, err_file, append)
    return None

def find_command_path(command: str) -> str | None:
    paths = os.environ.get('PATH', '').split(os.pathsep)
    for p in paths:
        file_path = f'{p}/{command}'
        if os.path.isfile(file_path) and os.access(file_path, os.X_OK):
            return p
    return None

class PathCommand(Command):
    def __init__(self, path: str, command: str, args: list[str], out_file: str, err_file:str, append: bool):
        super().__init__(args, out_file, err_file, append)
        self.path = path
        self.command = command
    
    def invoke(self) -> bool:
        full_args = [self.command] + self.args
        result = subprocess.run(
            full_args,
            cwd=self.path,
            capture_output=True,
            text=True
        )
        self.write_stdout(result.stdout, self.out_file, append=self.append)
        self.write_stderr(result.stderr, self.err_file, append=self.append)
        return True

class BackgroundPathCommand(Command):
    def __init__(self, path: str, command: str, args: list[str], out_file: str, err_file:str, append: bool):
        super().__init__(args, out_file, err_file, append)
        self.path = path
        self.command = command
    
    def invoke(self) -> bool:
        process = ManagedProcess(self.command, self.args)
        process.start(self.write_stdout_func(self.out_file, self.append), self.write_stderr_func(self.err_file, self.append))
        jobid = Backgrounder().register_job(process.get_pid(), self.command, self.args, process)
        self.write_stdout(f'[{jobid}] {process.get_pid()}\n', self.out_file, append=self.append)
        return True