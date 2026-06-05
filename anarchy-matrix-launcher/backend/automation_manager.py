# backend/automation_manager.py
from __future__ import annotations

try:
    from PySide6.QtCore import QObject, Signal, QThread
except ImportError:
    from PyQt5.QtCore import QObject, pyqtSignal as Signal, QThread


class _AutomationWorker(QObject):
    telemetryUpdated = Signal(str)
    tokenBalanceChanged = Signal(int)
    stateChanged = Signal(str)
    errorOccurred = Signal(str, str)

    def __init__(self) -> None:
        super().__init__()
        self._running = False
        self._tokens = 100

    def run(self) -> None:
        self.stateChanged.emit("Idle")

    def start(self) -> None:
        self._running = True
        self.stateChanged.emit("Running")
        self.telemetryUpdated.emit("[Automation] Routine initialized.")
        self.tokenBalanceChanged.emit(self._tokens)

    def stop(self) -> None:
        self._running = False
        self.stateChanged.emit("Idle")
        self.telemetryUpdated.emit("[Automation] Operations halted.")

    def command(self, text: str) -> None:
        if not self._running:
            self.telemetryUpdated.emit("[Automation] Ignored command (not running).")
            return
        self.telemetryUpdated.emit(f"[Automation] Command received: {text}")
        self._tokens = max(0, self._tokens - 1)
        self.tokenBalanceChanged.emit(self._tokens)


class AutomationManager(QObject):
    telemetryUpdated = Signal(str)
    tokenBalanceChanged = Signal(int)
    stateChanged = Signal(str)
    errorOccurred = Signal(str, str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._worker = _AutomationWorker()
        self._thread = QThread(self)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.telemetryUpdated.connect(self.telemetryUpdated)
        self._worker.tokenBalanceChanged.connect(self.tokenBalanceChanged)
        self._worker.stateChanged.connect(self.stateChanged)
        self._worker.errorOccurred.connect(self.errorOccurred)

        self._thread.start()

    def initialize(self) -> None:
        pass

    def start_automation(self) -> None:
        self._worker.start()

    def stop_automation(self) -> None:
        self._worker.stop()

    def send_command(self, text: str) -> None:
        self._worker.command(text)
