# backend/runtime_manager.py
from __future__ import annotations

from typing import List

try:
    from PySide6.QtCore import QObject, Signal, QThread
except ImportError:
    from PyQt5.QtCore import QObject, pyqtSignal as Signal, QThread

from ui.window import JavaRuntimeInfo


class _JavaDetectWorker(QObject):
    finished = Signal(list)
    errorOccurred = Signal(str, str)

    def run(self) -> None:
        try:
            # TODO: Detect Java runtimes on system and user space
            runtimes = [
                JavaRuntimeInfo("System JDK", "17.0.9", "/usr/lib/jvm/default"),
                JavaRuntimeInfo("User JDK 21", "21.0.1", "/home/user/.jvm/jdk-21"),
            ]
            self.finished.emit(runtimes)
        except Exception as exc:  # noqa: BLE001
            self.errorOccurred.emit("Java Detection Failed", str(exc))


class _JavaDownloadWorker(QObject):
    finished = Signal()
    errorOccurred = Signal(str, str)

    def __init__(self, version: str) -> None:
        super().__init__()
        self._version = version

    def run(self) -> None:
        try:
            # TODO: Download OpenJDK into user space
            print(f"[RuntimeManager] Downloading OpenJDK {self._version}...")
            self.finished.emit()
        except Exception as exc:  # noqa: BLE001
            self.errorOccurred.emit("Java Download Failed", str(exc))


class RuntimeManager(QObject):
    javaRuntimesUpdated = Signal(list)
    errorOccurred = Signal(str, str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._global_ram_mb = 4096
        self._instance_ram: dict[str, int] = {}
        self._active_runtime: str | None = None
        self._display_overrides: dict | None = None

    def detect_runtimes(self) -> None:
        worker = _JavaDetectWorker()
        thread = QThread(self)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.finished.connect(lambda rts: self._on_detect_finished(rts, thread, worker))
        worker.errorOccurred.connect(lambda t, m: self._on_error(t, m, thread, worker))

        thread.start()

    def _on_detect_finished(self, runtimes: List[JavaRuntimeInfo], thread: QThread, worker: QObject) -> None:
        thread.quit()
        thread.wait()
        worker.deleteLater()
        self.javaRuntimesUpdated.emit(runtimes)

    def set_global_ram(self, mb: int) -> None:
        self._global_ram_mb = mb
        print(f"[RuntimeManager] Global RAM set to {mb} MB")

    def set_instance_ram(self, name: str, mb: int) -> None:
        self._instance_ram[name] = mb
        print(f"[RuntimeManager] Instance {name} RAM set to {mb} MB")

    def set_active_runtime(self, runtime_label: str) -> None:
        self._active_runtime = runtime_label
        print(f"[RuntimeManager] Active runtime: {runtime_label}")

    def download_runtime(self, version: str) -> None:
        worker = _JavaDownloadWorker(version)
        thread = QThread(self)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.finished.connect(lambda: self._on_download_finished(thread, worker))
        worker.errorOccurred.connect(lambda t, m: self._on_error(t, m, thread, worker))

        thread.start()

    def _on_download_finished(self, thread: QThread, worker: QObject) -> None:
        thread.quit()
        thread.wait()
        worker.deleteLater()
        self.detect_runtimes()

    def set_display_overrides(self, cfg: dict) -> None:
        self._display_overrides = cfg
        print(f"[RuntimeManager] Display overrides: {cfg}")

    def _on_error(self, title: str, msg: str, thread: QThread, worker: QObject) -> None:
        thread.quit()
        thread.wait()
        worker.deleteLater()
        self.errorOccurred.emit(title, msg)
