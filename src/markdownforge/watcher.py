"""
File watcher for live reload
"""

import os
import time
import threading
from typing import Callable, Optional


class FileWatcher:
    """Simple file watcher for live reload"""

    def __init__(
        self,
        filepath: str,
        callback: Callable,
        interval: float = 1.0
    ):
        self.filepath = filepath
        self.callback = callback
        self.interval = interval
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._last_mtime: float = 0

    def start(self):
        """Start watching"""
        self._running = True
        self._last_mtime = self._get_mtime()
        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop watching"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)

    def _get_mtime(self) -> float:
        """Get file modification time"""
        try:
            return os.path.getmtime(self.filepath)
        except OSError:
            return 0

    def _watch_loop(self):
        """Main watch loop"""
        while self._running:
            current_mtime = self._get_mtime()
            if current_mtime != self._last_mtime:
                self._last_mtime = current_mtime
                self.callback()
            time.sleep(self.interval)
