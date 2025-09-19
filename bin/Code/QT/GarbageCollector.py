import gc
import threading
import time
from typing import Optional

from PySide2 import QtCore


class GarbageCollector(QtCore.QObject):

    def __init__(self, parent: Optional[QtCore.QObject] = None, interval_seconds: int = 30):
        super().__init__(parent)
        self.interval_seconds = int(interval_seconds)
        self._timer = QtCore.QTimer(self)
        self._timer.setInterval(self.interval_seconds * 1000)
        self._timer.setSingleShot(False)
        self._timer.timeout.connect(self._on_timeout)
        self._running = False
        self._lock = threading.Lock()
        self._worker_threads = []

    @QtCore.Slot()
    def _on_timeout(self):
        t = threading.Thread(target=self._run_collect_safe, daemon=True)
        t.start()
        self._worker_threads.append(t)

    def _run_collect_safe(self):
        with self._lock:
            try:
                gc.collect()

            except:
                pass

    def start(self):
        with self._lock:
            if self._running:
                return
            self._running = True
            self._timer.start()

    def stop(self, wait_workers_seconds: float = 2.0):
        with self._lock:
            if not self._running:
                return
            self._timer.stop()
            self._running = False
            deadline = time.time() + wait_workers_seconds
            for t in list(self._worker_threads):
                if not t.is_alive():
                    continue
                remaining = deadline - time.time()
                if remaining <= 0:
                    break
                t.join(timeout=remaining)
