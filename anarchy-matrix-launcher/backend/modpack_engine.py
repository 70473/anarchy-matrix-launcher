# backend/modpack_engine.py
from __future__ import annotations

try:
    from PySide6.QtCore import QObject, Signal, QThread
except ImportError:
    from PyQt5.QtCore import QObject, pyqtSignal as Signal, QThread

from ui.window import InstanceSummary


class _ModpackWorker(QObject):
    finished = Signal(InstanceSummary)
    errorOccurred = Signal(str, str)

    def __init__(self, manifest: str) -> None:
        super().__init__()
        self._manifest = manifest

    def run(self) -> None:
        try:
            # TODO: Parse manifest, download files, create instance directory
            summary = InstanceSummary(
                name="Imported Modpack",
                version="1.20.1",
                loader="Fabric",
                icon_path=None,
                last_launch="Never",
            )
            self.finished.emit(summary)
        except Exception as exc:  # noqa: BLE001
            self.errorOccurred.emit("Modpack Import Failed", str(exc))


class ModpackEngine(QObject):
    instanceCreated = Signal(InstanceSummary)
    errorOccurred = Signal(str, str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

    def ingest_manifest(self, manifest: str) -> None:
        worker = _ModpackWorker(manifest)
        thread = QThread(self)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.finished.connect(lambda summary: self._on_finished(summary, thread, worker))
        worker.errorOccurred.connect(lambda t, m: self._on_error(t, m, thread, worker))

        thread.start()

    def _on_finished(self, summary: InstanceSummary, thread: QThread, worker: QObject) -> None:
        thread.quit()
        thread.wait()
        worker.deleteLater()
        self.instanceCreated.emit(summary)

    def _on_error(self, title: str, msg: str, thread: QThread, worker: QObject) -> None:
        thread.quit()
        thread.wait()
        worker.deleteLater()
        self.errorOccurred.emit(title, msg)
