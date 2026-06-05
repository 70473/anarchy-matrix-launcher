# backend/identity_manager.py
from __future__ import annotations

from typing import List

try:
    from PySide6.QtCore import QObject, Signal
except ImportError:
    from PyQt5.QtCore import QObject, pyqtSignal as Signal


class IdentityManager(QObject):
    accountsUpdated = Signal(list)
    activeIdentityChanged = Signal(str, str)
    errorOccurred = Signal(str, str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._accounts: List[dict] = []
        self._active_id: str | None = None

    def refresh_accounts(self) -> None:
        # TODO: Load from secure storage / keyring
        self._accounts = [
            {"id": "ms-main", "name": "Main Microsoft", "type": "Microsoft", "active": True},
            {"id": "offline-dev", "name": "Dev Persona", "type": "Offline", "active": False},
        ]
        self._active_id = "ms-main"
        self.accountsUpdated.emit(self._accounts)
        self.activeIdentityChanged.emit("Main Microsoft", "Vanilla Cape")

    def switch_account(self, acc_id: str) -> None:
        for acc in self._accounts:
            acc["active"] = acc["id"] == acc_id
        self._active_id = acc_id
        self.accountsUpdated.emit(self._accounts)
        name = next((a["name"] for a in self._accounts if a["id"] == acc_id), "Unknown")
        self.activeIdentityChanged.emit(name, "Vanilla Cape")

    def add_offline_persona(self) -> None:
        # TODO: Prompt for name, create offline profile
        print("[IdentityManager] Add offline persona requested")

    def start_microsoft_oauth(self) -> None:
        # TODO: Launch OAuth flow in browser / embedded webview
        print("[IdentityManager] Microsoft OAuth flow requested")
