import threading


class Once:
    def __init__(self):
        self._lock = threading.Lock()
        self._done = False

    def do(self, func, *args, **kwargs):
        with self._lock:
            if not self._done:
                func(*args, **kwargs)
                self._done = True