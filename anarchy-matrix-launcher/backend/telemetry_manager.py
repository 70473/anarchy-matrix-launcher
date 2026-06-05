# backend/telemetry_manager.py
from __future__ import annotations

import subprocess
from typing import Optional

try:
    from PySide6.QtCore import QObject, Signal, QThread
except ImportError:
    from PyQt5.QtCore import QObject, pyqtSignal as Signal, QThread


class _LogExportWorker(QObject):
    finished = Signal(str)
    errorOccurred = Signal(str, str)

    def __init__(self, text: str) -> None:
        super().__init__()
        self._text = text

    def run(self) -> None:
        try:
            # TODO: POST to mclo.gs or similar
            url = "https://mclo.gs/example-crash-dump"
            self.finished.emit(url)
        except Exception as exc:  # noqa: BLE001
            self.errorOccurred.emit("Log Export Failed", str(exc))


class TelemetryManager(QObject):
    logLine = Signal(str, str)  # text, level
    logExported = Signal(str)
    errorOccurred = Signal(str, str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._process: Optional[subprocess.Popen] = None

    def attach_process(self, proc: subprocess.Popen) -> None:
        self._process = proc
        # TODO: Start QThread reading stdout/stderr and emitting logLine

    def kill_process(self) -> None:
        if self._process and self._process.poll() is None:
            try:
                self._process.kill()
                self.logLine.emit("[KILL] Game process terminated by user.", "error")
            except Exception as exc:  # noqa: BLE001
                self.errorOccurred.emit("Kill Failed", str(exc))

    def export_logs(self, text: str) -> None:
        worker = _LogExportWorker(text)
        thread = QThread(self)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.finished.connect(lambda url: self._on_export_finished(url, thread, worker))
        worker.errorOccurred.connect(lambda t, m: self._on_error(t, m, thread, worker))

        thread.start()

    def _on_export_finished(self, url: str, thread: QThread, worker: QObject) -> None:
        thread.quit()
        thread.wait()
        worker.deleteLater()
        self.logExported.emit(url)

    def _on_error(self, title: str, msg: str, thread: QThread, worker: QObject) -> None:
        thread.quit()
        thread.wait()
        worker.deleteLater()
        self.errorOccurred.emit(title, msg)
