from abc import ABC, abstractmethod
from app.backgrounder import Backgrounder
from app.managed_process import ManagedProcess

import os
import subprocess
import sys

class Command(ABC):
    @abstractmethod
    def invoke(self, args: list[str], out_file: str, err_file: str, append: bool) -> bool:
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

def find_command(command: str, background: bool) -> Command | None:
    from app.built_ins.registry import find_builtin
    c = find_builtin(command)
    if c:
        return c
    path = find_command_path(command)
    if path:
        if background:
            return BackgroundPathCommand(path, command)
        return PathCommand(path, command)
    return None

def find_command_path(command: str) -> str | None:
    paths = os.environ.get('PATH', '').split(os.pathsep)
    for p in paths:
        file_path = f'{p}/{command}'
        if os.path.isfile(file_path) and os.access(file_path, os.X_OK):
            return p
    return None

class PathCommand(Command):
    def __init__(self, path: str, command: str):
        self.path = path
        self.command = command
    
    def invoke(self, args: list[str], out_file: str, err_file: str, append: bool) -> bool:
        full_args = [self.command] + args
        result = subprocess.run(
            full_args,
            cwd=self.path,
            capture_output=True,
            text=True
        )
        self.write_stdout(result.stdout, out_file, append=append)
        self.write_stderr(result.stderr, err_file, append=append)
        return True

class BackgroundPathCommand(Command):
    def __init__(self, path: str, command: str):
        self.path = path
        self.command = command
    
    def invoke(self, args: list[str], out_file: str, err_file: str, append: bool) -> bool:
        self.run_background(self.command, args, out_file, err_file, append)
        return True

    def run_background(self, cmd, args, out_file, err_file, append):
        process = ManagedProcess(cmd, args)
        process.start(self.write_stdout_func(out_file, append), self.write_stderr_func(err_file, append))
        jobid = Backgrounder().register_job(process.get_pid(), cmd, args, process)
        self.write_stdout(f'[{jobid}] {process.get_pid()}\n', out_file)