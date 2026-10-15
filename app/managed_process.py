from app.debugger import Debugger
import subprocess
import threading

class ManagedProcess:
    def __init__(self, cmd: str, args: list[str]):
        self.cmd = cmd
        self.args = args
    
    def start(self, write_out: callable, write_err: callable):
        full_cmd = [self.cmd] + self.args
        self.process = subprocess.Popen(
            full_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        threading.Thread(target=self._stream_reader, args=(self.process.stdout, write_out), daemon=True).start()
        threading.Thread(target=self._stream_reader, args=(self.process.stderr, write_err), daemon=True).start()
    
    def _stream_reader(self, stream, write_content: callable):
        for line in stream:
            Debugger.debug(f'>>>> [{self.cmd} {self.args}] :: {line}')
            write_content(line)

    
    def get_pid(self):
        return self.process.pid

    def is_running(self) -> bool:
        if self.process is None:
            return False
        return self.process.poll() is None
    
    def get_exit_code(self) -> int | None:
        return self.process.poll() if self.process else None