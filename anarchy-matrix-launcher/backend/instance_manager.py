# backend/instance_manager.py
from __future__ import annotations

from typing import List

try:
    from PySide6.QtCore import QObject, Signal
except ImportError:
    from PyQt5.QtCore import QObject, pyqtSignal as Signal

from ui.window import InstanceSummary


class InstanceManager(QObject):
    instancesUpdated = Signal(list)
    instanceNamesUpdated = Signal(list)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._instances: List[InstanceSummary] = []

    def refresh_instances(self) -> None:
        # TODO: Replace with real discovery of instances from filesystem/config
        self._instances = [
            InstanceSummary("Dev Sandbox", "1.20.4", "Fabric", None, "2026-06-05 13:37"),
            InstanceSummary("Hardcore World", "1.19.4", "Fabric", None, "2026-06-04 22:10"),
            InstanceSummary("CyberChaos Pack", "1.18.2", "Fabric", None, "2026-06-01 18:05"),
        ]
        self.instancesUpdated.emit(self._instances)
        self.instanceNamesUpdated.emit([i.name for i in self._instances])

    def add_instance(self, summary: InstanceSummary) -> None:
        self._instances.append(summary)
        self.instancesUpdated.emit(self._instances)
        self.instanceNamesUpdated.emit([i.name for i in self._instances])

    def clone_instance(self, name: str) -> None:
        # TODO: Implement real cloning logic
        print(f"[InstanceManager] Clone requested for {name}")

    def export_instance_zip(self, name: str) -> None:
        # TODO: Implement real export logic
        print(f"[InstanceManager] Export ZIP requested for {name}")
