import os

class Debugger:
    debug_mode: bool = False
    debug_file = None

    def enable_debugging():
        Debugger.debug_mode = True
        Debugger.set_default_debug_file()

    def set_debug_file(file_path):
        Debugger.debug_file = file_path

    def set_default_debug_file():
        Debugger.set_debug_file('~/tmp/debug.out')

    def debug(msg):
        if Debugger.debug_mode and Debugger.debug_file:
            debug_file_normalized = str.replace(Debugger.debug_file, '~', os.environ.get('HOME'))
            with open(debug_file_normalized, 'a') as file:
                file.write(msg)
                file.write('\n')