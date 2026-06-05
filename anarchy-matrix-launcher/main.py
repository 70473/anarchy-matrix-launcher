# main.py
from __future__ import annotations

import sys

from backend.instance_manager import InstanceManager
from backend.modpack_engine import ModpackEngine
from backend.repo_client import AddonRepositoryClient
from backend.identity_manager import IdentityManager
from backend.runtime_manager import RuntimeManager
from backend.telemetry_manager import TelemetryManager
from backend.automation_manager import AutomationManager

from ui.window import create_app_and_window


def wire_backend(window) -> None:
    """
    Wire UI signals to backend services.
    This is intentionally thin: all heavy work is in backend modules,
    and all long-running tasks must be threaded there.
    """

    # --- Instantiate backend services ---------------------------------------
    instance_mgr = InstanceManager()
    modpack_engine = ModpackEngine()
    repo_client = AddonRepositoryClient()
    identity_mgr = IdentityManager()
    runtime_mgr = RuntimeManager()
    telemetry_mgr = TelemetryManager()
    automation_mgr = AutomationManager()

    # --- INSTANCE MATRIX & MODPACK HUB --------------------------------------
    ip = window.instance_panel

    ip.requestInstanceRefresh.connect(instance_mgr.refresh_instances)
    instance_mgr.instancesUpdated.connect(ip.set_instances)

    ip.requestModpackImport.connect(modpack_engine.ingest_manifest)
    modpack_engine.instanceCreated.connect(instance_mgr.add_instance)

    ip.requestInstanceClone.connect(instance_mgr.clone_instance)
    ip.requestInstanceExport.connect(instance_mgr.export_instance_zip)

    # --- ADD-ON REPOSITORY & DEP SOLVER -------------------------------------
    ap = window.addon_panel

    ap.requestSearch.connect(repo_client.search_addons)
    repo_client.searchResults.connect(ap.set_results)

    ap.requestInstallAddon.connect(repo_client.install_addon)
    ap.requestResolveDeps.connect(repo_client.resolve_dependencies)
    repo_client.dependencyReport.connect(ap.show_dependency_warnings)

    # --- IDENTITY CONTROL CENTER --------------------------------------------
    idp = window.identity_panel

    idp.requestAccountRefresh.connect(identity_mgr.refresh_accounts)
    identity_mgr.accountsUpdated.connect(idp.set_accounts)

    idp.requestSwitchAccount.connect(identity_mgr.switch_account)
    identity_mgr.activeIdentityChanged.connect(
        lambda name, cape: idp.set_active_identity(name, cape)
    )

    idp.requestAddOfflinePersona.connect(identity_mgr.add_offline_persona)
    idp.requestOpenAuthFlow.connect(identity_mgr.start_microsoft_oauth)

    # --- SYSTEM TUNING & RUNTIME MANAGEMENT ---------------------------------
    sp = window.system_panel

    instance_mgr.instanceNamesUpdated.connect(sp.set_instances)

    sp.ramGlobalChanged.connect(runtime_mgr.set_global_ram)
    sp.ramInstanceChanged.connect(runtime_mgr.set_instance_ram)

    runtime_mgr.javaRuntimesUpdated.connect(sp.set_java_runtimes)
    sp.javaRuntimeSelected.connect(runtime_mgr.set_active_runtime)
    sp.requestJavaDownload.connect(runtime_mgr.download_runtime)

    sp.displayOverrideChanged.connect(runtime_mgr.set_display_overrides)

    # --- ENGINE TELEMETRY & LIFECYCLE CONTROLS ------------------------------
    tp = window.telemetry_panel

    telemetry_mgr.logLine.connect(tp.append_log_line)
    tp.requestKillProcess.connect(telemetry_mgr.kill_process)
    tp.requestLogExport.connect(telemetry_mgr.export_logs)

    telemetry_mgr.logExported.connect(
        lambda url: window.show_info("Log Exported", f"Crash logs uploaded:\n{url}")
    )
    telemetry_mgr.errorOccurred.connect(
        lambda title, msg: window.show_error(title, msg)
    )

    # --- IN-GAME AI BOT AUTOMATION CONTROL DECK ------------------------------
    apanel = window.automation_panel

    apanel.requestAutomationStart.connect(automation_mgr.start_automation)
    apanel.requestAutomationStop.connect(automation_mgr.stop_automation)
    apanel.requestAutomationCommand.connect(automation_mgr.send_command)

    automation_mgr.stateChanged.connect(apanel.set_state)
    automation_mgr.telemetryUpdated.connect(apanel.append_telemetry)
    automation_mgr.tokenBalanceChanged.connect(apanel.set_token_balance)

    # --- Cross-service bootstraps -------------------------------------------
    instance_mgr.refresh_instances()
    identity_mgr.refresh_accounts()
    runtime_mgr.detect_runtimes()
    automation_mgr.initialize()


def main() -> None:
    app, window = create_app_and_window()
    wire_backend(window)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
