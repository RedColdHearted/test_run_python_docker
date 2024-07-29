import os
import signal

pid = 1
os.kill(pid, signal.SIGTERM)
