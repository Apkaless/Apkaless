import os
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class TweakResult:
    success: bool
    message: str


class SystemTweaker:
    """Windows system tweaks and utilities with safety guards.

    Notes:
    - Most operations require Administrator privileges
    - Where risky, a system restore point is attempted beforehand
    - All methods return TweakResult for clear feedback
    """

    def __init__(self, create_restore_points: bool = True) -> None:
        self.create_restore_points = create_restore_points

    # ------------------------- Helpers -------------------------
    def _is_admin(self) -> bool:
        try:
            import ctypes
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            return False

    def _run(self, cmd: str, timeout: int = 60) -> Tuple[bool, str]:
        try:
            proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
            if proc.returncode == 0:
                return True, (proc.stdout or '').strip()
            return False, (proc.stderr or proc.stdout or 'Unknown error').strip()
        except subprocess.TimeoutExpired:
            return False, f"Command timed out after {timeout}s: {cmd}"
        except Exception as e:
            return False, str(e)

    def _checkpoint(self, name: str) -> None:
        if not self.create_restore_points:
            return
        # Best-effort restore point. Ignore failures so tweaks can continue.
        self._run(f'powershell.exe -NoProfile -Command "try {{ Checkpoint-Computer -Description \"{name}\" -RestorePointType \"MODIFY_SETTINGS\" }} catch {{ }}"')

    # ------------------------- Network Tweaks -------------------------
    def flush_dns(self) -> TweakResult:
        ok, msg = self._run('ipconfig /flushdns')
        return TweakResult(ok, 'DNS cache flushed' if ok else f'Flush DNS failed: {msg}')

    def reset_winsock(self) -> TweakResult:
        if not self._is_admin():
            return TweakResult(False, 'Administrator privileges are required to reset Winsock')
        self._checkpoint('Apkaless_ResetWinsock')
        ok, msg = self._run('netsh winsock reset')
        return TweakResult(ok, 'Winsock reset. Reboot recommended.' if ok else f'Winsock reset failed: {msg}')

    def reset_ip_stack(self) -> TweakResult:
        if not self._is_admin():
            return TweakResult(False, 'Administrator privileges are required to reset IP stack')
        self._checkpoint('Apkaless_ResetIP')
        ok1, msg1 = self._run('netsh int ip reset')
        ok2, msg2 = self._run('netsh int ipv6 reset')
        ok = ok1 and ok2
        if ok:
            return TweakResult(True, 'IP stack reset (IPv4/IPv6). Reboot recommended.')
        return TweakResult(False, f'IP reset had issues: IPv4="{msg1}" IPv6="{msg2}"')

    def set_dns_for_all_adapters(self, primary: str, secondary: Optional[str] = None) -> List[TweakResult]:
        """Set DNS on all active Ethernet/Wi-Fi adapters by name match.
        Uses netsh to apply statically configured DNS servers.
        """
        if not self._is_admin():
            return [TweakResult(False, 'Administrator privileges are required to set DNS')]
        self._checkpoint('Apkaless_SetDNS')

        results: List[TweakResult] = []
        # Query adapter names
        ok, output = self._run('netsh interface show interface | findstr /R /C:"Enabled"')
        if not ok:
            return [TweakResult(False, f'Could not enumerate interfaces: {output}')]

        adapter_names: List[str] = []
        for line in output.splitlines():
            # Example: Enabled    Connected    Dedicated    Wi-Fi
            parts = [p for p in line.strip().split(' ') if p]
            if parts:
                name = line.split()[-1]
                if name.lower() in ['wi-fi', 'wifi', 'ethernet', 'ethernet0']:
                    adapter_names.append(name)

        if not adapter_names:
            # Fallback: try common names regardless of state
            adapter_names = ['Wi-Fi', 'Ethernet', 'Ethernet0']

        for name in adapter_names:
            ok1, msg1 = self._run(f'netsh interface ip set dns name="{name}" source=static addr={primary} register=PRIMARY')
            if secondary:
                ok2, msg2 = self._run(f'netsh interface ip add dns name="{name}" addr={secondary} index=2')
            else:
                ok2, msg2 = True, ''
            if ok1 and ok2:
                results.append(TweakResult(True, f'Set DNS {primary}{"/"+secondary if secondary else ""} on {name}'))
            else:
                results.append(TweakResult(False, f'Failed DNS set on {name}: {msg1 or msg2}'))
        return results

    def optimize_tcp(self) -> List[TweakResult]:
        """Apply conservative TCP tweaks aimed at throughput without being aggressive.
        Keys are under HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters.
        """
        if not self._is_admin():
            return [TweakResult(False, 'Administrator privileges are required for TCP optimization')]
        self._checkpoint('Apkaless_TCPOptimize')

        tweaks = [
            (r'"HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters"', 'Tcp1323Opts', 'REG_DWORD', '1'),
            (r'"HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters"', 'TcpTimedWaitDelay', 'REG_DWORD', '30'),
            (r'"HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters"', 'MaxUserPort', 'REG_DWORD', '65534'),
        ]

        results: List[TweakResult] = []
        for key, name, typ, value in tweaks:
            ok, msg = self._run(f'reg add {key} /v {name} /t {typ} /d {value} /f')
            results.append(TweakResult(ok, f'{name} set' if ok else f'{name} failed: {msg}'))
        return results

    # ------------------------- Services -------------------------
    def set_service_start(self, service_name: str, start_mode: str) -> TweakResult:
        """Set service start mode: auto, demand, disabled.
        start_mode should be one of: auto|demand|disabled
        """
        if not self._is_admin():
            return TweakResult(False, 'Administrator privileges are required to change services')
        if start_mode not in ['auto', 'demand', 'disabled']:
            return TweakResult(False, 'start_mode must be auto|demand|disabled')
        self._checkpoint(f'Apkaless_Service_{service_name}_{start_mode}')
        ok, msg = self._run(f'sc config "{service_name}" start= {start_mode}')
        return TweakResult(ok, f'{service_name} set to {start_mode}' if ok else f'Failed to update {service_name}: {msg}')

    def stop_service(self, service_name: str) -> TweakResult:
        if not self._is_admin():
            return TweakResult(False, 'Administrator privileges are required to stop services')
        ok, msg = self._run(f'net stop "{service_name}"')
        return TweakResult(ok, f'{service_name} stopped' if ok else f'Failed to stop {service_name}: {msg}')

    def start_service(self, service_name: str) -> TweakResult:
        if not self._is_admin():
            return TweakResult(False, 'Administrator privileges are required to start services')
        ok, msg = self._run(f'net start "{service_name}"')
        return TweakResult(ok, f'{service_name} started' if ok else f'Failed to start {service_name}: {msg}')

    # ------------------------- Privacy Tweaks -------------------------
    def apply_privacy_tweaks(self) -> List[TweakResult]:
        """Apply conservative Windows privacy tweaks (telemetry off where possible)."""
        if not self._is_admin():
            return [TweakResult(False, 'Administrator privileges are required for privacy tweaks')]
        self._checkpoint('Apkaless_PrivacyTweaks')

        results: List[TweakResult] = []
        reg_ops = [
            # Disable telemetry (where supported)
            (r'"HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection"', 'AllowTelemetry', 'REG_DWORD', '0'),
            # Disable tailored experiences
            (r'"HKLM\SOFTWARE\Policies\Microsoft\Windows\CloudContent"', 'DisableTailoredExperiencesWithDiagnosticData', 'REG_DWORD', '1'),
            # Disable advertising ID
            (r'"HKLM\SOFTWARE\Policies\Microsoft\Windows\AdvertisingInfo"', 'DisabledByGroupPolicy', 'REG_DWORD', '1'),
        ]
        for key, name, typ, value in reg_ops:
            ok, msg = self._run(f'reg add {key} /v {name} /t {typ} /d {value} /f')
            results.append(TweakResult(ok, f'{name} applied' if ok else f'{name} failed: {msg}'))

        # Disable some telemetry-related services (best effort)
        for svc in ['DiagTrack', 'dmwappushservice']:
            results.append(self.set_service_start(svc, 'disabled'))
            results.append(self.stop_service(svc))
        return results

    def revert_privacy_tweaks(self) -> List[TweakResult]:
        if not self._is_admin():
            return [TweakResult(False, 'Administrator privileges are required to revert tweaks')]
        self._checkpoint('Apkaless_RevertPrivacyTweaks')
        results: List[TweakResult] = []
        # Re-enable services to default (demand)
        for svc in ['DiagTrack', 'dmwappushservice']:
            results.append(self.set_service_start(svc, 'demand'))
            results.append(self.start_service(svc))
        # Remove/relax policy keys (best effort)
        to_del = [
            (r'"HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection"', 'AllowTelemetry'),
            (r'"HKLM\SOFTWARE\Policies\Microsoft\Windows\CloudContent"', 'DisableTailoredExperiencesWithDiagnosticData'),
            (r'"HKLM\SOFTWARE\Policies\Microsoft\Windows\AdvertisingInfo"', 'DisabledByGroupPolicy'),
        ]
        for key, name in to_del:
            ok, msg = self._run(f'reg delete {key} /v {name} /f')
            # Success or already deleted is fine
            results.append(TweakResult(ok or ('The system was unable to find' in msg), f'{name} removed'))
        return results

    # ------------------------- Cleanup -------------------------
    def clear_temp_files(self) -> TweakResult:
        try:
            temp_paths = [
                os.environ.get('TEMP', ''),
                os.environ.get('TMP', ''),
                os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Local', 'Temp'),
                os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Local', 'Microsoft', 'Windows', 'INetCache'),
                os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Local', 'Microsoft', 'Windows', 'WebCache'),
            ]
            removed = 0
            for root in temp_paths:
                if not root or not os.path.exists(root):
                    continue
                for entry in os.listdir(root):
                    path = os.path.join(root, entry)
                    try:
                        if os.path.isfile(path):
                            os.unlink(path)
                            removed += 1
                        elif os.path.isdir(path):
                            import shutil
                            shutil.rmtree(path, ignore_errors=True)
                            removed += 1
                    except Exception:
                        continue
            return TweakResult(True, f'Cleared ~{removed} temporary items')
        except Exception as e:
            return TweakResult(False, f'Cleanup failed: {e}')

    # ------------------------- Debloaters -------------------------
    def debloat_edge(self) -> List[TweakResult]:
        """Best-effort Microsoft Edge debloater.
        Disables Edge update services/tasks and attempts a forced uninstall.
        Some systems may block uninstall; we still disable updates.
        """
        if not self._is_admin():
            return [TweakResult(False, 'Administrator privileges are required to modify Edge')] 
        self._checkpoint('Apkaless_Debloat_Edge')

        results: List[TweakResult] = []
        # Disable Edge update services
        for svc in ['edgeupdate', 'edgeupdatem']:
            ok1, msg1 = self._run(f'sc stop {svc}')
            ok2, msg2 = self._run(f'sc config {svc} start= disabled')
            results.append(TweakResult(ok1 or 'has not been started' in msg1.lower(), f'{svc} stop: {msg1 or "ok"}'))
            results.append(TweakResult(ok2, f'{svc} disabled' if ok2 else f'{svc} disable failed: {msg2}'))

        # Disable scheduled tasks
        edge_tasks = [
            r"\Microsoft\Edge\UpdateTaskMachineCore",
            r"\Microsoft\Edge\UpdateTaskMachineUA",
            r"\MicrosoftEdgeUpdateTaskMachineCore",
            r"\MicrosoftEdgeUpdateTaskMachineUA",
        ]
        for task in edge_tasks:
            ok, msg = self._run(f'schtasks /Change /TN "{task}" /Disable')
            results.append(TweakResult(ok or 'cannot find the file specified' in (msg or '').lower(), f'Task {task} disabled' if ok else f'Task {task} disable: {msg or "not found"}'))

        # Attempt uninstall (system-level)
        # Search common installer paths for setup.exe
        setup_paths = [
            r'%ProgramFiles(x86)%\Microsoft\Edge\Application',
            r'%ProgramFiles%\Microsoft\Edge\Application'
        ]
        found_setup = False
        for base in setup_paths:
            # List directories and try Installer\setup.exe
            ok, listing = self._run(f'cmd /c for /d %G in ("{base}\\*") do @if exist "%G\\Installer\\setup.exe" echo %G')
            if ok and listing:
                for line in listing.splitlines():
                    inst_path = f'"{line}\\Installer\\setup.exe"'
                    oku, msgu = self._run(f'{inst_path} --uninstall --system-level --force-uninstall')
                    results.append(TweakResult(oku, 'Edge uninstall attempted (system-level)' if oku else f'Edge uninstall attempt failed: {msgu}'))
                    found_setup = True
                    break
            if found_setup:
                break
        if not found_setup:
            results.append(TweakResult(False, 'Edge setup.exe not found; skipped uninstall step'))

        return results

    def disable_copilot(self) -> List[TweakResult]:
        """Disable Windows Copilot via policy and UI registry. Best effort, requires admin for HKLM."""
        results: List[TweakResult] = []
        if not self._is_admin():
            return [TweakResult(False, 'Administrator privileges are required to disable Copilot')]
        self._checkpoint('Apkaless_Disable_Copilot')

        # Policy to turn off Copilot
        ok1, msg1 = self._run(r'reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot" /v TurnOffWindowsCopilot /t REG_DWORD /d 1 /f')
        results.append(TweakResult(ok1, 'Policy TurnOffWindowsCopilot=1' if ok1 else f'Policy set failed: {msg1}'))

        # Hide taskbar Copilot button for current user
        ok2, msg2 = self._run(r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v ShowCopilotButton /t REG_DWORD /d 0 /f')
        results.append(TweakResult(ok2, 'Taskbar Copilot button hidden' if ok2 else f'Hide button failed: {msg2}'))

        # Optional: attempt to remove Web Experience Pack (may power Copilot features)
        # Best effort; may fail if not present
        ok3, msg3 = self._run('powershell -NoProfile -Command "try { Get-AppxPackage -AllUsers MicrosoftWindows.Client.WebExperience | Remove-AppxPackage -ErrorAction Stop; Write-Output \"WebExperience removed\" } catch { Write-Output $_.Exception.Message }"', timeout=180)
        results.append(TweakResult(True, msg3 or 'WebExperience removal attempted'))

        return results


# ------------------------- Simple CLI for standalone testing -------------------------

def main() -> None:
    tw = SystemTweaker()

    menu = (
        "\nSystem Tweaker (Windows)\n"
        "=" * 28 + "\n"
        "1) Flush DNS\n"
        "2) Reset Winsock (admin)\n"
        "3) Reset IP Stack (admin)\n"
        "4) Set DNS for adapters (admin)\n"
        "5) Optimize TCP (admin)\n"
        "6) Apply Privacy Tweaks (admin)\n"
        "7) Revert Privacy Tweaks (admin)\n"
        "8) Clear Temp Files\n"
        "9) Debloat Microsoft Edge (admin)\n"
        "10) Disable Windows Copilot (admin)\n"
        "11) Exit\n"
    )

    while True:
        print(menu)
        choice = input('Select option: ').strip()
        if choice == '1':
            print(tw.flush_dns())
        elif choice == '2':
            print(tw.reset_winsock())
        elif choice == '3':
            print(tw.reset_ip_stack())
        elif choice == '4':
            p = input('Primary DNS (e.g., 1.1.1.1): ').strip()
            s = input('Secondary DNS (optional): ').strip() or None
            for res in tw.set_dns_for_all_adapters(p, s):
                print(res)
        elif choice == '5':
            for res in tw.optimize_tcp():
                print(res)
        elif choice == '6':
            for res in tw.apply_privacy_tweaks():
                print(res)
        elif choice == '7':
            for res in tw.revert_privacy_tweaks():
                print(res)
        elif choice == '8':
            print(tw.clear_temp_files())
        elif choice == '9':
            for res in tw.debloat_edge():
                print(res)
        elif choice == '10':
            for res in tw.disable_copilot():
                print(res)
        elif choice == '11':
            break
        else:
            print('Invalid option')
        time.sleep(1)


if __name__ == '__main__':
    main()
