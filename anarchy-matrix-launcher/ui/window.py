# ui/window.py
from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Optional, List

try:
    from PySide6.QtCore import Qt, QSize, Signal, QObject, QThread
    from PySide6.QtGui import QIcon, QAction, QTextCursor, QColor, QFont
    from PySide6.QtWidgets import (
        QApplication,
        QMainWindow,
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QStackedWidget,
        QListWidget,
        QListWidgetItem,
        QLabel,
        QPushButton,
        QFrame,
        QGridLayout,
        QLineEdit,
        QTextEdit,
        QScrollArea,
        QSlider,
        QComboBox,
        QSpinBox,
        QFormLayout,
        QGroupBox,
        QProgressBar,
        QMessageBox,
        QSizePolicy,
    )
    QT_LIB = "PySide6"
except ImportError:  # Fallback to PyQt5
    from PyQt5.QtCore import Qt, QSize, pyqtSignal as Signal, QObject, QThread
    from PyQt5.QtGui import QIcon, QAction, QTextCursor, QColor, QFont
    from PyQt5.QtWidgets import (
        QApplication,
        QMainWindow,
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QStackedWidget,
        QListWidget,
        QListWidgetItem,
        QLabel,
        QPushButton,
        QFrame,
        QGridLayout,
        QLineEdit,
        QTextEdit,
        QScrollArea,
        QSlider,
        QComboBox,
        QSpinBox,
        QFormLayout,
        QGroupBox,
        QProgressBar,
        QMessageBox,
        QSizePolicy,
    )
    QT_LIB = "PyQt5"


class Theme:
    WINDOW_BG = "#0A0A0C"
    CARD_BG = "#141419"
    ACCENT = "#8A2BE2"
    CYAN = "#00FFFF"
    SUCCESS = "#39FF14"
    TERMINAL = "#FF3131"
    TEXT_PRIMARY = "#F5F5F7"
    TEXT_MUTED = "#9A9AA2"
    WARNING = "#FFD700"
    ERROR = "#FF3131"

    @staticmethod
    def apply(app: QApplication) -> None:
        app.setStyleSheet(f"""
            QMainWindow {{
                background-color: {Theme.WINDOW_BG};
            }}
            QWidget {{
                color: {Theme.TEXT_PRIMARY};
                background-color: {Theme.WINDOW_BG};
                font-family: "JetBrains Mono", "Fira Code", monospace;
                font-size: 11pt;
            }}
            QFrame#Card {{
                background-color: {Theme.CARD_BG};
                border-radius: 8px;
                border: 1px solid #1F1F26;
            }}
            QListWidget {{
                background-color: #050507;
                border: none;
                color: {Theme.TEXT_PRIMARY};
            }}
            QListWidget::item {{
                padding: 10px;
            }}
            QListWidget::item:selected {{
                background-color: {Theme.ACCENT};
                color: #FFFFFF;
            }}
            QPushButton {{
                background-color: {Theme.CARD_BG};
                border-radius: 6px;
                border: 1px solid #262633;
                padding: 6px 12px;
                color: {Theme.TEXT_PRIMARY};
            }}
            QPushButton:hover {{
                border-color: {Theme.CYAN};
            }}
            QPushButton:pressed {{
                background-color: #0F0F14;
            }}
            QPushButton[accent="true"] {{
                background-color: {Theme.ACCENT};
                border-color: {Theme.ACCENT};
                color: #FFFFFF;
            }}
            QPushButton[accent="true"]:hover {{
                background-color: #9D3BFF;
            }}
            QLineEdit, QTextEdit, QComboBox {{
                background-color: #050507;
                border-radius: 4px;
                border: 1px solid #262633;
                padding: 4px 6px;
                color: {Theme.TEXT_PRIMARY};
            }}
            QSlider::groove:horizontal {{
                border: 1px solid #262633;
                height: 6px;
                background: #050507;
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {Theme.ACCENT};
                border: 1px solid #000000;
                width: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }}
            QProgressBar {{
                border: 1px solid #262633;
                border-radius: 4px;
                background: #050507;
                text-align: center;
                color: {Theme.TEXT_PRIMARY};
            }}
            QProgressBar::chunk {{
                background-color: {Theme.CYAN};
            }}
        """)


@dataclass
class InstanceSummary:
    name: str
    version: str
    loader: str
    icon_path: Optional[str]
    last_launch: str


@dataclass
class JavaRuntimeInfo:
    name: str
    version: str
    path: str


class WorkerBase(QObject):
    errorOccurred = Signal(str, str)


class LogUploadWorker(WorkerBase):
    finished = Signal(str)

    def __init__(self, log_text: str, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._log_text = log_text

    def run(self) -> None:
        try:
            url = "https://mclo.gs/example-crash-dump"
            self.finished.emit(url)
        except Exception as exc:  # noqa: BLE001
            self.errorOccurred.emit("Log Upload Failed", str(exc))


def create_card(parent: Optional[QWidget] = None) -> QFrame:
    card = QFrame(parent)
    card.setObjectName("Card")
    card.setFrameShape(QFrame.StyledPanel)
    card.setFrameShadow(QFrame.Raised)
    return card


def set_accent_button(btn: QPushButton) -> None:
    btn.setProperty("accent", True)
    btn.style().unpolish(btn)
    btn.style().polish(btn)


class InstanceMatrixPanel(QWidget):
    requestInstanceRefresh = Signal()
    requestModpackImport = Signal(str)
    requestInstanceClone = Signal(str)
    requestInstanceExport = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._instances: List[InstanceSummary] = []
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        header = QLabel("INSTANCE MATRIX & MODPACK HUB")
        header.setStyleSheet(f"color: {Theme.ACCENT}; font-size: 14pt; font-weight: 600;")
        root.addWidget(header)

        controls_card = create_card(self)
        controls_layout = QHBoxLayout(controls_card)
        controls_layout.setContentsMargins(10, 10, 10, 10)
        controls_layout.setSpacing(8)

        self.refresh_btn = QPushButton("Refresh Instances")
        set_accent_button(self.refresh_btn)
        self.refresh_btn.clicked.connect(self.requestInstanceRefresh.emit)

        self.modpack_input = QLineEdit()
        self.modpack_input.setPlaceholderText(
            "Paste Modrinth / CurseForge / FTB / Technic manifest URL or local path..."
        )
        self.modpack_import_btn = QPushButton("Ingest Modpack")
        set_accent_button(self.modpack_import_btn)
        self.modpack_import_btn.clicked.connect(self._on_modpack_import)

        controls_layout.addWidget(self.refresh_btn)
        controls_layout.addWidget(self.modpack_input, 1)
        controls_layout.addWidget(self.modpack_import_btn)

        root.addWidget(controls_card)

        grid_card = create_card(self)
        grid_layout = QVBoxLayout(grid_card)
        grid_layout.setContentsMargins(10, 10, 10, 10)
        grid_layout.setSpacing(8)

        grid_header = QLabel("Isolated Sandboxed Installations")
        grid_header.setStyleSheet(f"color: {Theme.TEXT_MUTED}; font-weight: 500;")
        grid_layout.addWidget(grid_header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setHorizontalSpacing(10)
        self.grid_layout.setVerticalSpacing(10)
        scroll.setWidget(self.grid_container)

        grid_layout.addWidget(scroll)
        root.addWidget(grid_card, 1)

    def set_instances(self, instances: List[InstanceSummary]) -> None:
        self._instances = instances
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        cols = 3
        for idx, inst in enumerate(instances):
            row = idx // cols
            col = idx % cols
            card = self._create_instance_card(inst)
            self.grid_layout.addWidget(card, row, col)

    def _create_instance_card(self, inst: InstanceSummary) -> QWidget:
        card = create_card(self)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        title = QLabel(inst.name)
        title.setStyleSheet("font-weight: 600;")
        layout.addWidget(title)

        meta = QLabel(f"Version: {inst.version}  •  Loader: {inst.loader}")
        meta.setStyleSheet(f"color: {Theme.TEXT_MUTED}; font-size: 9pt;")
        layout.addWidget(meta)

        last = QLabel(f"Last Launch: {inst.last_launch}")
        last.setStyleSheet(f"color: {Theme.TEXT_MUTED}; font-size: 9pt;")
        layout.addWidget(last)

        btn_row = QHBoxLayout()
        clone_btn = QPushButton("Clone Config")
        export_btn = QPushButton("Export ZIP")
        clone_btn.clicked.connect(lambda: self.requestInstanceClone.emit(inst.name))
        export_btn.clicked.connect(lambda: self.requestInstanceExport.emit(inst.name))
        btn_row.addWidget(clone_btn)
        btn_row.addWidget(export_btn)
        layout.addLayout(btn_row)

        return card

    def _on_modpack_import(self) -> None:
        text = self.modpack_input.text().strip()
        if not text:
            QMessageBox.warning(self, "No Manifest", "Please provide a manifest URL or path.")
            return
        self.requestModpackImport.emit(text)


class AddonRepositoryPanel(QWidget):
    requestSearch = Signal(str)
    requestInstallAddon = Signal(str)
    requestResolveDeps = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        header = QLabel("IN-LAUNCHER ADD-ON REPOSITORY & DEPENDENCY SOLVER")
        header.setStyleSheet(f"color: {Theme.ACCENT}; font-size: 14pt; font-weight: 600;")
        root.addWidget(header)

        search_card = create_card(self)
        search_layout = QHBoxLayout(search_card)
        search_layout.setContentsMargins(10, 10, 10, 10)
        search_layout.setSpacing(8)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search Modrinth / CurseForge for Mods, Resource Packs, Shaders...")
        self.search_btn = QPushButton("Search")
        set_accent_button(self.search_btn)
        self.search_btn.clicked.connect(self._on_search)

        search_layout.addWidget(self.search_input, 1)
        search_layout.addWidget(self.search_btn)
        root.addWidget(search_card)

        body = QHBoxLayout()
        root.addLayout(body, 1)

        results_card = create_card(self)
        results_layout = QVBoxLayout(results_card)
        results_layout.setContentsMargins(10, 10, 10, 10)
        results_layout.setSpacing(6)

        results_label = QLabel("Repository Browser")
        results_label.setStyleSheet(f"color: {Theme.TEXT_MUTED}; font-weight: 500;")
        results_layout.addWidget(results_label)

        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self._on_install_selected)
        results_layout.addWidget(self.results_list, 1)

        body.addWidget(results_card, 2)

        deps_card = create_card(self)
        deps_layout = QVBoxLayout(deps_card)
        deps_layout.setContentsMargins(10, 10, 10, 10)
        deps_layout.setSpacing(6)

        deps_label = QLabel("Dependency Auto-Resolver")
        deps_label.setStyleSheet(f"color: {Theme.TEXT_MUTED}; font-weight: 500;")
        deps_layout.addWidget(deps_label)

        self.deps_alert = QTextEdit()
        self.deps_alert.setReadOnly(True)
        self.deps_alert.setPlaceholderText(
            "Missing mod prerequisites will appear here and be scheduled for automatic download..."
        )
        deps_layout.addWidget(self.deps_alert, 1)

        self.resolve_btn = QPushButton("Resolve & Install Dependencies")
        set_accent_button(self.resolve_btn)
        self.resolve_btn.clicked.connect(self._on_resolve_deps)
        deps_layout.addWidget(self.resolve_btn)

        body.addWidget(deps_card, 3)

    def set_results(self, items: List[dict]) -> None:
        self.results_list.clear()
        for it in items:
            text = f"{it.get('name', 'Unknown')}  •  {it.get('type', '')}  •  {it.get('source', '')}"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, it.get("id"))
            self.results_list.addItem(item)

    def show_dependency_warnings(self, text: str) -> None:
        self.deps_alert.setPlainText(text)

    def _on_search(self) -> None:
        query = self.search_input.text().strip()
        if not query:
            return
        self.requestSearch.emit(query)

    def _on_install_selected(self, item: QListWidgetItem) -> None:
        addon_id = item.data(Qt.UserRole)
        if addon_id:
            self.requestInstallAddon.emit(addon_id)

    def _on_resolve_deps(self) -> None:
        item = self.results_list.currentItem()
        if not item:
            QMessageBox.information(self, "No Selection", "Select an add-on to resolve dependencies for.")
            return
        addon_id = item.data(Qt.UserRole)
        if addon_id:
            self.requestResolveDeps.emit(addon_id)


class IdentityControlPanel(QWidget):
    requestAccountRefresh = Signal()
    requestSwitchAccount = Signal(str)
    requestAddOfflinePersona = Signal()
    requestOpenAuthFlow = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        left_card = create_card(self)
        left_layout = QVBoxLayout(left_card)
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_layout.setSpacing(6)

        header = QLabel("IDENTITY CONTROL CENTER")
        header.setStyleSheet(f"color: {Theme.ACCENT}; font-size: 14pt; font-weight: 600;")
        left_layout.addWidget(header)

        self.accounts_list = QListWidget()
        self.accounts_list.itemDoubleClicked.connect(self._on_switch_account)
        left_layout.addWidget(self.accounts_list, 1)

        btn_row = QHBoxLayout()
        self.refresh_btn = QPushButton("Refresh Accounts")
        self.refresh_btn.clicked.connect(self.requestAccountRefresh.emit)
        self.add_offline_btn = QPushButton("Add Offline Persona")
        self.add_offline_btn.clicked.connect(self.requestAddOfflinePersona.emit)
        self.ms_auth_btn = QPushButton("Microsoft OAuth Login")
        set_accent_button(self.ms_auth_btn)
        self.ms_auth_btn.clicked.connect(self.requestOpenAuthFlow.emit)

        btn_row.addWidget(self.refresh_btn)
        btn_row.addWidget(self.add_offline_btn)
        btn_row.addWidget(self.ms_auth_btn)
        left_layout.addLayout(btn_row)

        root.addWidget(left_card, 2)

        right_card = create_card(self)
        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(8)

        active_label = QLabel("Active Player Profile")
        active_label.setStyleSheet(f"color: {Theme.TEXT_MUTED}; font-weight: 500;")
        right_layout.addWidget(active_label)

        self.skin_preview = QLabel("Skin Preview")
        self.skin_preview.setAlignment(Qt.AlignCenter)
        self.skin_preview.setMinimumSize(200, 260)
        self.skin_preview.setStyleSheet(
            "border-radius: 6px; border: 1px dashed #333344; background-color: #050507;"
        )
        right_layout.addWidget(self.skin_preview, 1)

        self.cape_label = QLabel("Active Cape: None")
        self.cape_label.setStyleSheet(f"color: {Theme.TEXT_MUTED};")
        right_layout.addWidget(self.cape_label)

        root.addWidget(right_card, 3)

    def set_accounts(self, accounts: List[dict]) -> None:
        self.accounts_list.clear()
        for acc in accounts:
            prefix = "● " if acc.get("active") else "○ "
            text = f"{prefix}{acc.get('name', 'Unknown')}  •  {acc.get('type', '')}"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, acc.get("id"))
            self.accounts_list.addItem(item)

    def set_active_identity(self, name: str, cape: str) -> None:
        self.skin_preview.setText(name)
        self.cape_label.setText(f"Active Cape: {cape or 'None'}")

    def _on_switch_account(self, item: QListWidgetItem) -> None:
        acc_id = item.data(Qt.UserRole)
        if acc_id:
            self.requestSwitchAccount.emit(acc_id)


class SystemTuningPanel(QWidget):
    ramGlobalChanged = Signal(int)
    ramInstanceChanged = Signal(str, int)
    javaRuntimeSelected = Signal(str)
    requestJavaDownload = Signal(str)
    displayOverrideChanged = Signal(dict)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        header = QLabel("SYSTEM TUNING & RUNTIME MANAGEMENT")
        header.setStyleSheet(f"color: {Theme.ACCENT}; font-size: 14pt; font-weight: 600;")
        root.addWidget(header)

        ram_card = create_card(self)
        ram_layout = QFormLayout(ram_card)
        ram_layout.setContentsMargins(10, 10, 10, 10)
        ram_layout.setSpacing(8)

        self.global_ram_slider = QSlider(Qt.Horizontal)
        self.global_ram_slider.setRange(512, 16384)
        self.global_ram_slider.setSingleStep(256)
        self.global_ram_slider.valueChanged.connect(self._on_global_ram_changed)
        self.global_ram_label = QLabel("Global Max Heap: 4096 MB")
        ram_layout.addRow(self.global_ram_label, self.global_ram_slider)

        self.instance_selector = QComboBox()
        self.instance_ram_slider = QSlider(Qt.Horizontal)
        self.instance_ram_slider.setRange(512, 16384)
        self.instance_ram_slider.setSingleStep(256)
        self.instance_ram_slider.valueChanged.connect(self._on_instance_ram_changed)
        self.instance_ram_label = QLabel("Per-Instance Max Heap: 4096 MB")
        ram_layout.addRow(self.instance_selector, self.instance_ram_label)
        ram_layout.addRow(QLabel("Instance Heap Slider"), self.instance_ram_slider)

        root.addWidget(ram_card)

        java_card = create_card(self)
        java_layout = QHBoxLayout(java_card)
        java_layout.setContentsMargins(10, 10, 10, 10)
        java_layout.setSpacing(8)

        self.java_combo = QComboBox()
        self.java_combo.currentTextChanged.connect(self.javaRuntimeSelected.emit)
        java_layout.addWidget(QLabel("Java Runtime:"))
        java_layout.addWidget(self.java_combo, 1)

        self.download_java_8 = QPushButton("Download OpenJDK 8")
        self.download_java_17 = QPushButton("Download OpenJDK 17")
        self.download_java_21 = QPushButton("Download OpenJDK 21")
        self.download_java_8.clicked.connect(lambda: self.requestJavaDownload.emit("8"))
        self.download_java_17.clicked.connect(lambda: self.requestJavaDownload.emit("17"))
        self.download_java_21.clicked.connect(lambda: self.requestJavaDownload.emit("21"))

        java_layout.addWidget(self.download_java_8)
        java_layout.addWidget(self.download_java_17)
        java_layout.addWidget(self.download_java_21)

        root.addWidget(java_card)

        display_card = create_card(self)
        display_layout = QFormLayout(display_card)
        display_layout.setContentsMargins(10, 10, 10, 10)
        display_layout.setSpacing(8)

        self.res_width = QSpinBox()
        self.res_width.setRange(640, 7680)
        self.res_width.setValue(1920)
        self.res_height = QSpinBox()
        self.res_height.setRange(480, 4320)
        self.res_height.setValue(1080)
        self.jvm_flags = QLineEdit()
        self.jvm_flags.setPlaceholderText("Custom JVM flags (e.g., -XX:+UseG1GC -XX:+UnlockExperimentalVMOptions)")

        display_layout.addRow("Width:", self.res_width)
        display_layout.addRow("Height:", self.res_height)
        display_layout.addRow("JVM Flags:", self.jvm_flags)

        self.apply_display_btn = QPushButton("Apply Display Overrides")
        set_accent_button(self.apply_display_btn)
        self.apply_display_btn.clicked.connect(self._on_display_changed)
        display_layout.addRow(self.apply_display_btn)

        root.addWidget(display_card)

    def set_instances(self, names: List[str]) -> None:
        self.instance_selector.clear()
        self.instance_selector.addItems(names)

    def set_java_runtimes(self, runtimes: List[JavaRuntimeInfo]) -> None:
        self.java_combo.clear()
        for rt in runtimes:
            self.java_combo.addItem(f"{rt.name} ({rt.version})", rt.path)

    def _on_global_ram_changed(self, value: int) -> None:
        self.global_ram_label.setText(f"Global Max Heap: {value} MB")
        self.ramGlobalChanged.emit(value)

    def _on_instance_ram_changed(self, value: int) -> None:
        self.instance_ram_label.setText(f"Per-Instance Max Heap: {value} MB")
        inst_name = self.instance_selector.currentText()
        if inst_name:
            self.ramInstanceChanged.emit(inst_name, value)

    def _on_display_changed(self) -> None:
        cfg = {
            "width": self.res_width.value(),
            "height": self.res_height.value(),
            "jvm_flags": self.jvm_flags.text().strip(),
        }
        self.displayOverrideChanged.emit(cfg)


class TelemetryPanel(QWidget):
    requestKillProcess = Signal()
    requestLogExport = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        header = QLabel("ENGINE TELEMETRY & LIFECYCLE CONTROLS")
        header.setStyleSheet(f"color: {Theme.ACCENT}; font-size: 14pt; font-weight: 600;")
        root.addWidget(header)

        term_card = create_card(self)
        term_layout = QVBoxLayout(term_card)
        term_layout.setContentsMargins(10, 10, 10, 10)
        term_layout.setSpacing(6)

        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        font = QFont("JetBrains Mono", 10)
        self.terminal.setFont(font)
        self.terminal.setStyleSheet(
            f"background-color: #050507; color: {Theme.CYAN}; border-radius: 6px; border: 1px solid #262633;"
        )
        term_layout.addWidget(self.terminal, 1)

        root.addWidget(term_card, 1)

        controls_card = create_card(self)
        controls_layout = QHBoxLayout(controls_card)
        controls_layout.setContentsMargins(10, 10, 10, 10)
        controls_layout.setSpacing(8)

        self.export_btn = QPushButton("Export Crash Logs")
        set_accent_button(self.export_btn)
        self.export_btn.clicked.connect(self._on_export_logs)

        self.kill_btn = QPushButton("EMERGENCY KILL SWITCH")
        self.kill_btn.setStyleSheet(
            f"background-color: {Theme.ERROR}; color: #FFFFFF; font-weight: 700; border-radius: 6px;"
        )
        self.kill_btn.clicked.connect(self.requestKillProcess.emit)

        controls_layout.addWidget(self.export_btn)
        controls_layout.addStretch(1)
        controls_layout.addWidget(self.kill_btn)

        root.addWidget(controls_card)

    def append_log_line(self, line: str, level: str = "info") -> None:
        color = Theme.CYAN
        if level == "warn":
            color = Theme.WARNING
        elif level == "error":
            color = Theme.TERMINAL

        cursor = self.terminal.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.terminal.setTextCursor(cursor)

        self.terminal.setTextColor(QColor(color))
        self.terminal.insertPlainText(line.rstrip() + "\n")
        self.terminal.moveCursor(QTextCursor.End)

    def _on_export_logs(self) -> None:
        text = self.terminal.toPlainText()
        if not text.strip():
            QMessageBox.information(self, "No Logs", "There is no log output to export.")
            return
        self.requestLogExport.emit(text)


class AutomationPanel(QWidget):
    requestAutomationStart = Signal()
    requestAutomationStop = Signal()
    requestAutomationCommand = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        header = QLabel("IN-GAME AI BOT AUTOMATION CONTROL DECK")
        header.setStyleSheet(f"color: {Theme.ACCENT}; font-size: 14pt; font-weight: 600;")
        root.addWidget(header)

        top_layout = QHBoxLayout()
        root.addLayout(top_layout, 1)

        core_card = create_card(self)
        core_layout = QVBoxLayout(core_card)
        core_layout.setContentsMargins(10, 10, 10, 10)
        core_layout.setSpacing(6)

        core_label = QLabel("Core Machine Interface")
        core_label.setStyleSheet(f"color: {Theme.TEXT_MUTED}; font-weight: 500;")
        core_layout.addWidget(core_label)

        self.state_label = QLabel("State: Idle")
        self.state_label.setStyleSheet(f"color: {Theme.TEXT_MUTED};")
        core_layout.addWidget(self.state_label)

        self.telemetry_view = QTextEdit()
        self.telemetry_view.setReadOnly(True)
        self.telemetry_view.setPlaceholderText("Automation runner telemetry stream...")
        core_layout.addWidget(self.telemetry_view, 1)

        top_layout.addWidget(core_card, 3)

        resource_card = create_card(self)
        resource_layout = QVBoxLayout(resource_card)
        resource_layout.setContentsMargins(10, 10, 10, 10)
        resource_layout.setSpacing(6)

        resource_label = QLabel("Execution Tokens")
        resource_label.setStyleSheet(f"color: {Theme.TEXT_MUTED}; font-weight: 500;")
        resource_layout.addWidget(resource_label)

        self.token_progress = QProgressBar()
        self.token_progress.setRange(0, 100)
        self.token_progress.setValue(100)
        resource_layout.addWidget(self.token_progress)

        self.token_label = QLabel("Remaining: 100%")
        self.token_label.setStyleSheet(f"color: {Theme.SUCCESS}; font-weight: 600;")
        resource_layout.addWidget(self.token_label)

        top_layout.addWidget(resource_card, 2)

        toggle_card = create_card(self)
        toggle_layout = QHBoxLayout(toggle_card)
        toggle_layout.setContentsMargins(10, 10, 10, 10)
        toggle_layout.setSpacing(8)

        self.start_btn = QPushButton("Initialize Routine")
        set_accent_button(self.start_btn)
        self.start_btn.clicked.connect(self._on_start)

        self.stop_btn = QPushButton("Halt Operations")
        self.stop_btn.clicked.connect(self._on_stop)

        toggle_layout.addWidget(self.start_btn)
        toggle_layout.addWidget(self.stop_btn)

        root.addWidget(toggle_card)

        directives_card = create_card(self)
        directives_layout = QHBoxLayout(directives_card)
        directives_layout.setContentsMargins(10, 10, 10, 10)
        directives_layout.setSpacing(8)

        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Enter natural language directive for the automation bot...")
        self.command_input.returnPressed.connect(self._on_send_command)

        self.send_command_btn = QPushButton("Send Directive")
        set_accent_button(self.send_command_btn)
        self.send_command_btn.clicked.connect(self._on_send_command)

        directives_layout.addWidget(self.command_input, 1)
        directives_layout.addWidget(self.send_command_btn)

        root.addWidget(directives_card)

    def set_state(self, text: str) -> None:
        self.state_label.setText(f"State: {text}")

    def append_telemetry(self, text: str) -> None:
        self.telemetry_view.append(text)

    def set_token_balance(self, percent: int) -> None:
        percent = max(0, min(100, percent))
        self.token_progress.setValue(percent)
        self.token_label.setText(f"Remaining: {percent}%")
        if percent < 20:
            self.token_label.setStyleSheet(f"color: {Theme.ERROR}; font-weight: 600;")
        else:
            self.token_label.setStyleSheet(f"color: {Theme.SUCCESS}; font-weight: 600;")

    def _on_start(self) -> None:
        self.requestAutomationStart.emit()

    def _on_stop(self) -> None:
        self.requestAutomationStop.emit()

    def _on_send_command(self) -> None:
        text = self.command_input.text().strip()
        if not text:
            return
        self.requestAutomationCommand.emit(text)
        self.command_input.clear()


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Anarchy Matrix - Minecraft Instance Orchestrator")
        self.resize(1400, 850)
        self._build_ui()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.nav_list = QListWidget()
        self.nav_list.setFixedWidth(260)
        self.nav_list.setSpacing(2)
        self.nav_list.setSelectionMode(QListWidget.SingleSelection)

        sections = [
            "Instance Matrix & Modpack Hub",
            "Add-on Repository & Dependency Solver",
            "Identity Control Center",
            "System Tuning & Runtime Management",
            "Engine Telemetry & Lifecycle Controls",
            "In-Game AI Bot Automation Deck",
        ]
        for name in sections:
            item = QListWidgetItem(name)
            item.setSizeHint(QSize(240, 40))
            self.nav_list.addItem(item)

        root.addWidget(self.nav_list)

        self.stack = QStackedWidget()
        root.addWidget(self.stack, 1)

        self.instance_panel = InstanceMatrixPanel()
        self.addon_panel = AddonRepositoryPanel()
        self.identity_panel = IdentityControlPanel()
        self.system_panel = SystemTuningPanel()
        self.telemetry_panel = TelemetryPanel()
        self.automation_panel = AutomationPanel()

        self.stack.addWidget(self.instance_panel)
        self.stack.addWidget(self.addon_panel)
        self.stack.addWidget(self.identity_panel)
        self.stack.addWidget(self.system_panel)
        self.stack.addWidget(self.telemetry_panel)
        self.stack.addWidget(self.automation_panel)

        self.nav_list.setCurrentRow(0)
        self.stack.setCurrentIndex(0)
        self.nav_list.currentRowChanged.connect(self.stack.setCurrentIndex)

        self._build_menu()

    def _build_menu(self) -> None:
        file_menu = self.menuBar().addMenu("&File")
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

    def show_info(self, title: str, msg: str) -> None:
        QMessageBox.information(self, title, msg)

    def show_error(self, title: str, msg: str) -> None:
        QMessageBox.critical(self, title, msg)


def create_app_and_window():
    app = QApplication.instance() or QApplication(sys.argv)
    Theme.apply(app)
    win = MainWindow()
    return app, win
