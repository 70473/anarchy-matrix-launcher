# backend/repo_client.py
from __future__ import annotations

from typing import List

try:
    from PySide6.QtCore import QObject, Signal, QThread
except ImportError:
    from PyQt5.QtCore import QObject, pyqtSignal as Signal, QThread


class _SearchWorker(QObject):
    finished = Signal(list)
    errorOccurred = Signal(str, str)

    def __init__(self, query: str) -> None:
        super().__init__()
        self._query = query

    def run(self) -> None:
        try:
            # TODO: Call Modrinth / CurseForge APIs
            results = [
                {"id": "modrinth-example", "name": "Cyber Blades", "source": "Modrinth", "type": "Mod"},
                {"id": "curseforge-example", "name": "Neon Shaders", "source": "CurseForge", "type": "Shader"},
            ]
            self.finished.emit(results)
        except Exception as exc:  # noqa: BLE001
            self.errorOccurred.emit("Search Failed", str(exc))


class _DepsWorker(QObject):
    finished = Signal(str)
    errorOccurred = Signal(str, str)

    def __init__(self, addon_id: str) -> None:
        super().__init__()
        self._addon_id = addon_id

    def run(self) -> None:
        try:
            # TODO: Resolve dependencies via API
            text = f"Dependencies for {self._addon_id}:\n - fabric-api\n - cloth-config\nAll will be installed automatically."
            self.finished.emit(text)
        except Exception as exc:  # noqa: BLE001
            self.errorOccurred.emit("Dependency Resolution Failed", str(exc))


class AddonRepositoryClient(QObject):
    searchResults = Signal(list)
    dependencyReport = Signal(str)
    errorOccurred = Signal(str, str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

    def search_addons(self, query: str) -> None:
        worker = _SearchWorker(query)
        thread = QThread(self)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.finished.connect(lambda res: self._on_search_finished(res, thread, worker))
        worker.errorOccurred.connect(lambda t, m: self._on_error(t, m, thread, worker))

        thread.start()

    def _on_search_finished(self, results: List[dict], thread: QThread, worker: QObject) -> None:
        thread.quit()
        thread.wait()
        worker.deleteLater()
        self.searchResults.emit(results)

    def resolve_dependencies(self, addon_id: str) -> None:
        worker = _DepsWorker(addon_id)
        thread = QThread(self)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.finished.connect(lambda text: self._on_deps_finished(text, thread, worker))
        worker.errorOccurred.connect(lambda t, m: self._on_error(t, m, thread, worker))

        thread.start()

    def _on_deps_finished(self, text: str, thread: QThread, worker: QObject) -> None:
        thread.quit()
        thread.wait()
        worker.deleteLater()
        self.dependencyReport.emit(text)

    def install_addon(self, addon_id: str) -> None:
        # TODO: Download and install selected addon
        print(f"[AddonRepositoryClient] Install addon {addon_id}")

    def _on_error(self, title: str, msg: str, thread: QThread, worker: QObject) -> None:
        thread.quit()
        thread.wait()
        worker.deleteLater()
        self.errorOccurred.emit(title, msg)
