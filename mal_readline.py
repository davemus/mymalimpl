import os
import readline
import atexit


history_file = os.path.expanduser('~/.mal_history')
os.system(f'touch {history_file}')
readline.set_auto_history(True)
readline.set_history_length(1000)
readline.read_history_file(history_file)


atexit.register(readline.write_history_file, history_file)
