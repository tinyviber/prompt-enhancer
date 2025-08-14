import threading

class StateManager:
    def __init__(self):
        self._enabled = False
        self._lock = threading.Lock()

    def set_enabled(self, status: bool):
        with self._lock:
            self._enabled = status

    def is_enabled(self) -> bool:
        with self._lock:
            return self._enabled

state_manager = StateManager()