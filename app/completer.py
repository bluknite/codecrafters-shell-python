from app.debugger import Debugger
from pathlib import Path

import os
import readline
import subprocess
import sys

class Completer():
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            Debugger.debug('>> Creating new Completer instance')
            cls._instance = super().__new__(cls)
        else:
            Debugger.debug('>> Using existing Completer instance')
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.completions = {}
            self.initialized = True
    
    def has_completer(self, command) -> bool:
        return command in self.completions.keys()
    
    def register_completer(self, command, path) -> None:
        self.completions[command] = path
    
    def get_completer_path(self, command) -> str | None:
        return self.completions.get(command, None)
    
    def register_hooks(self):
        readline.set_completer(self.invoke_completion)
        readline.set_completer_delims(" \t\n`!@#$%^&*()=+[{]}\\|;:'\",<>?")
        readline.set_completion_display_matches_hook(self.display_matches_hook)
        readline.parse_and_bind("tab: complete")
        readline.parse_and_bind("set bell-style audible")
        readline.parse_and_bind("set show-all-if-ambiguous off")
    
    def invoke_completion(self, text: str, state: int) -> str:
        buffer = readline.get_line_buffer()
        begidx = readline.get_begidx()
        prefix = buffer[:begidx]
        is_first_word = prefix.strip() == ""

        Debugger.debug(f'Completion invoked with text: {text} and state: {state}')
        Debugger.debug(f'~~ Buffer: >{buffer}<')
        Debugger.debug(f'~~ BegIdx: >{begidx}<')
        Debugger.debug(f'~~ Prefix: >{prefix}<')
        Debugger.debug(f'~~ IsFirstWord: {is_first_word}')

        def find_matching_entries(entries: list[str], prefix: str) -> list[str]:
            if len(prefix) == 0:
                return entries
            return [e for e in entries if e.startswith(prefix)]

        def find_matching_command():
            from app.built_ins.registry import built_ins, registered_commands
            Debugger.debug(f'Searching for {text}...')
            COMMANDS = registered_commands()
            matches = find_matching_entries(COMMANDS, text)
            Debugger.debug(f'~~~ Matches found in built-ins for {text}: {matches}')
            try:
                return f'{matches[state]} '
            except IndexError:
                if len(matches) > 0:
                    return None

            Debugger.debug(f'~~~ Searching in PATH for {text}...')
            all_matches = []
            for p in os.environ.get('PATH', '').split(os.pathsep):
                Debugger.debug(f'~~~ Searching in PATH for {text}: {p}')
                if os.path.isdir(p):
                    with os.scandir(p) as entries:
                        files = [entry.name for entry in entries if entry.is_file()]
                        all_matches.extend(find_matching_entries(files, text))
            Debugger.debug(f'~~~ Matches found in PATH for {text}: {all_matches}')
            try:
                return f'{all_matches[state]} '
            except IndexError:
                pass
            
            return None
        
        def find_matching_path_entries():
            cwd = Path.cwd()
            slash_idx = text.rfind('/')
            if slash_idx == -1:
                path = ''
                prefix = text
            else:
                path = text[:slash_idx+1]
                prefix = text[slash_idx+1:]
            full_path = os.path.join(cwd, path)
            with os.scandir(full_path) as entries:
                matches = [(path + entry.name, entry.is_dir()) for entry in entries if entry.name.startswith(prefix)]
                formatted_matches = [f'{m}{"/" if is_dir else " "}' for (m, is_dir) in matches]
                Debugger.debug(f'~~~ Matches found in current directory for {text}: {formatted_matches}')
                try:
                    return f'{formatted_matches[state]}'
                except IndexError:
                    if len(matches) > 0:
                        return None
        
        Debugger.debug(f'~~~ Beginning command search...')
        if is_first_word:
            return find_matching_command()

        command = prefix.strip()
        if (command.find(" ") == -1) and (len(text.strip()) == 0):
            # first completion after a command with no arguments
            completer_path = self.get_completer_path(command)
            Debugger.debug(f'~~~ Completer path for {command} -> {completer_path}')
            if completer_path:
                options = self.invoke_completer(completer_path)
                if options:
                    matches = find_matching_entries(options, text)
                    Debugger.debug(f'~~~ Matches found in completer for {text}: {matches}')
                    try:
                        return f'{matches[state]} '
                    except IndexError:
                        if len(matches) > 0:
                            return None

        return find_matching_path_entries()

    def display_matches_hook(self, substitution: str, matches: list, max_length: int):
        buffer = readline.get_line_buffer()
        begidx = readline.get_begidx()
        prefix = buffer[:begidx]
        sys.stdout.write("\n")
        sys.stdout.write("  ".join(matches))
        sys.stdout.write(f'\n$ {prefix}{substitution}')
        sys.stdout.flush()
        readline.redisplay()
    
    def invoke_completer(self, path: str) -> list[str] | None:
        exec_path = Path(path)
        try:
            result = subprocess.run(
                [str(exec_path)],
                cwd=exec_path.parent,
                capture_output=True,
                text=True,
                check=True,
                timeout=2
            )
            return [e for e in result.stdout.split('\n') if len(e) > 0]
        except subprocess.CalledProcessError as e:
            # Triggered if check=True and the exit code is non-zero
            Debugger.debug(f'~~~ Subprocess failed with exit code {e.returncode}')
            Debugger.debug(f'~~~ Stderr: {e.stderr}')
            Debugger.debug(f'~~~ Stdout: {e.stdout}')

        except subprocess.TimeoutExpired as e:
            # Triggered if the process takes longer than 2 seconds
            Debugger.debug(f'~~~ Subprocess timed out after 2 seconds!')
            if e.stderr:
                Debugger.debug(f'~~~ Partial Stderr: {e.stderr}')
        except Exception as e:
            Debugger.debug(f'~~~ Subprocess failed with exception: {e}')
        return None
    