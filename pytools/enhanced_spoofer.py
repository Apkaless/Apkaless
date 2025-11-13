import os
import sys
import random
import string
import subprocess
from urllib import request
import psutil
import winreg
import hashlib
import time
import shutil
from datetime import datetime
from pathlib import Path
import urllib
import bs4
import requests

class EnhancedSpoofer:
    def __init__(self):
        self.backup_dir = "spoofer_backups"
        self.log_file = "spoofer_log.txt"
        self.max_backups = 50  # Maximum number of backup files to keep
        self.ensure_backup_dir()
        
    def ensure_backup_dir(self):
        """Create backup directory if it doesn't exist"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            
    def log_action(self, action, status, details=""):
        """Log all spoofing actions"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {action}: {status} {details}\n"
        
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"⚠️ Warning: Could not write to log file: {e}")
            
    def cleanup_old_backups(self):
        """Remove old backup files to prevent disk space issues"""
        try:
            if os.path.exists(self.backup_dir):
                backup_files = [f for f in os.listdir(self.backup_dir) if f.endswith('.reg')]
                if len(backup_files) > self.max_backups:
                    # Sort by modification time (oldest first)
                    backup_files.sort(key=lambda x: os.path.getmtime(os.path.join(self.backup_dir, x)))
                    
                    # Remove oldest files
                    files_to_remove = backup_files[:-self.max_backups]
                    for old_file in files_to_remove:
                        try:
                            os.remove(os.path.join(self.backup_dir, old_file))
                            self.log_action("Backup Cleanup", "SUCCESS", f"Removed old backup: {old_file}")
                        except Exception as e:
                            self.log_action("Backup Cleanup", "ERROR", f"Failed to remove {old_file}: {e}")
                            
        except Exception as e:
            self.log_action("Backup Cleanup", "ERROR", str(e))
            
            
    def create_system_restore(self):
        """Create a system restore point before spoofing"""
        try:
            restore_name = f"Apkaless_Spoofer_Backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            cmd = f'powershell.exe -Command "Checkpoint-Computer -Description \'{restore_name}\' -RestorePointType \'MODIFY_SETTINGS\'"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_action("System Restore Point", "SUCCESS", f"Created: {restore_name}")
                return True
            else:
                self.log_action("System Restore Point", "FAILED", result.stderr)
                return False
        except Exception as e:
            self.log_action("System Restore Point", "ERROR", str(e))
            return False
            
    def backup_registry_key(self, key_path, key_name):
        """Backup a registry key before modification"""
        try:
            # Ensure key_path has the full registry path
            if not key_path.startswith('HKEY_'):
                if key_path.startswith('SOFTWARE\\'):
                    full_key_path = f"HKEY_LOCAL_MACHINE\\{key_path}"
                elif key_path.startswith('SYSTEM\\'):
                    full_key_path = f"HKEY_LOCAL_MACHINE\\{key_path}"
                else:
                    full_key_path = f"HKEY_LOCAL_MACHINE\\{key_path}"
            else:
                full_key_path = key_path
                
            # Generate unique backup filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]  # Include milliseconds
            backup_file = os.path.join(self.backup_dir, f"{key_name}_{timestamp}.reg")
            
            # Create backup using reg export
            cmd = f'reg export "{full_key_path}" "{backup_file}" /y'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Verify backup file was created
                if os.path.exists(backup_file):
                    self.log_action(f"Registry Backup {key_name}", "SUCCESS", backup_file)
                    # Cleanup old backups
                    self.cleanup_old_backups()
                    return True
                else:
                    self.log_action(f"Registry Backup {key_name}", "FAILED", "Backup file validation failed")
                    # Remove invalid backup file
                    if os.path.exists(backup_file):
                        try:
                            os.remove(backup_file)
                        except:
                            pass
                    return False
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                self.log_action(f"Registry Backup {key_name}", "FAILED", error_msg)
                return False
                
        except Exception as e:
            self.log_action(f"Registry Backup {key_name}", "ERROR", str(e))
            return False
    
    def backup_registry_value(self, key_path, value_name):
        """Backup a specific registry value before modification"""
        try:
            # Ensure key_path has the full registry path
            if not key_path.startswith('HKEY_'):
                if key_path.startswith('SOFTWARE\\'):
                    full_key_path = f"HKEY_LOCAL_MACHINE\\{key_path}"
                elif key_path.startswith('SYSTEM\\'):
                    full_key_path = f"HKEY_LOCAL_MACHINE\\{key_path}"
                else:
                    full_key_path = f"HKEY_LOCAL_MACHINE\\{key_path}"
            else:
                full_key_path = key_path
                
            # Generate unique backup filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
            backup_file = os.path.join(self.backup_dir, f"{value_name}_{timestamp}.reg")
            
            # Create backup using reg export
            cmd = f'reg export "{full_key_path}" "{backup_file}" /y'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Verify backup file was created
                if os.path.exists(backup_file):
                    self.log_action(f"Registry Value Backup {value_name}", "SUCCESS", backup_file)
                    
                    # Cleanup old backups
                    self.cleanup_old_backups()
                    
                    return True
                else:
                    self.log_action(f"Registry Value Backup {value_name}", "FAILED", "Backup file validation failed")
                    # Remove invalid backup file
                    if os.path.exists(backup_file):
                        try:
                            os.remove(backup_file)
                        except:
                            pass
                    return False
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                self.log_action(f"Registry Value Backup {value_name}", "FAILED", error_msg)
                return False
                
        except Exception as e:
            self.log_action(f"Registry Value Backup {value_name}", "ERROR", str(e))
            return False
            
    def generate_random_hwid(self, length=8):
        """Generate a random hardware ID"""
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
        
    def generate_machine_guid(self):
        """Generate a new machine GUID"""
        guid_parts = [
            self.generate_random_hwid(8),
            self.generate_random_hwid(4),
            self.generate_random_hwid(4),
            self.generate_random_hwid(4),
            self.generate_random_hwid(12)
        ]
        return '-'.join(guid_parts).lower()
        
    def generate_product_id(self):
        """Generate a new product ID"""
        return '-'.join([self.generate_random_hwid(5) for _ in range(4)])
        
    def spoof_machine_guid(self):
        """Spoof the machine GUID in registry"""
        try:
            key_path = r"SOFTWARE\Microsoft\Cryptography"
            key_name = "MachineGuid"
            new_guid = self.generate_machine_guid()
            
            # Backup current value
            self.backup_registry_key(key_path, key_name)
            
            # Modify registry
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, key_name, 0, winreg.REG_SZ, new_guid)
                
            self.log_action("Machine GUID Spoof", "SUCCESS", f"New GUID: {new_guid}")
            return True
        except Exception as e:
            self.log_action("Machine GUID Spoof", "ERROR", str(e))
            return False
            
    def spoof_product_id(self):
        """Spoof the product ID in registry"""
        try:
            key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
            key_name = "ProductId"
            new_product_id = self.generate_product_id()
            
            # Backup current value
            self.backup_registry_key(key_path, key_name)
            
            # Modify registry
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, key_name, 0, winreg.REG_SZ, new_product_id)
                
            self.log_action("Product ID Spoof", "SUCCESS", f"New ID: {new_product_id}")
            return True
        except Exception as e:
            self.log_action("Product ID Spoof", "ERROR", str(e))
            return False
            
    def spoof_hw_profile_guid(self):
        """Spoof the hardware profile GUID"""
        try:
            key_path = r"SYSTEM\CurrentControlSet\Control\IDConfigDB\Hardware Profiles\0001"
            key_name = "HwProfileGuid"
            new_guid = "{" + self.generate_machine_guid() + "}"
            
            # Backup current value
            self.backup_registry_key(key_path, key_name)
            
            # Modify registry
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, key_name, 0, winreg.REG_SZ, new_guid)
                
            self.log_action("HW Profile GUID Spoof", "SUCCESS", f"New GUID: {new_guid}")
            return True
        except Exception as e:
            self.log_action("HW Profile GUID Spoof", "ERROR", str(e))
            return False
            
    def spoof_machine_id(self):
        """Spoof the machine ID in SQM client"""
        try:
            key_path = r"SOFTWARE\Microsoft\SQMClient"
            key_name = "MachineId"
            new_machine_id = self.generate_machine_guid()
            
            # Backup current value
            self.backup_registry_key(key_path, key_name)
            
            # Modify registry
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, key_name, 0, winreg.REG_SZ, new_machine_id)
                
            self.log_action("Machine ID Spoof", "SUCCESS", f"New ID: {new_machine_id}")
            return True
        except Exception as e:
            self.log_action("Machine ID Spoof", "ERROR", str(e))
            return False
            
    def spoof_mac_address(self):
        """Spoof MAC address of network adapters"""
        try:
            # Get network interfaces
            interfaces = psutil.net_if_addrs()
            spoofed_count = 0
            
            for interface_name, addresses in interfaces.items():
                if interface_name in ['Ethernet', 'Wi-Fi', 'Ethernet0']:
                    try:
                        # Generate new MAC address
                        new_mac = ':'.join([f"{random.randint(0, 255):02x}" for _ in range(6)])
                        
                        # Find registry key for this interface
                        cmd = f'reg query "HKEY_LOCAL_MACHINE\\SYSTEM\\ControlSet001\\Control\\Class\\{{4d36e972-e325-11ce-bfc1-08002be10318}}" /s /f "{interface_name}"'
                        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                        
                        if result.returncode == 0:
                            # Extract the interface number and spoof MAC
                            for line in result.stdout.split('\n'):
                                if 'HKEY_LOCAL_MACHINE' in line and '\\000' in line:
                                    interface_key = line.strip()
                                    spoof_cmd = f'reg add "{interface_key}" /v NetworkAddress /d {new_mac.replace(":", "")} /f'
                                    spoof_result = subprocess.run(spoof_cmd, shell=True, capture_output=True, text=True)
                                    
                                    if 'The operation completed successfully' in spoof_result.stdout:
                                        spoofed_count += 1
                                        self.log_action(f"MAC Spoof {interface_name}", "SUCCESS", f"New MAC: {new_mac}")
                                    else:
                                        self.log_action(f"MAC Spoof {interface_name}", "FAILED", spoof_result.stderr)
                    except Exception as e:
                        self.log_action(f"MAC Spoof {interface_name}", "ERROR", str(e))
                        
            if spoofed_count > 0:
                self.log_action("MAC Address Spoofing", "SUCCESS", f"Spoofed {spoofed_count} interfaces")
                return True
            else:
                self.log_action("MAC Address Spoofing", "FAILED", "No interfaces were spoofed")
                return False
                
        except Exception as e:
            self.log_action("MAC Address Spoofing", "ERROR", str(e))
            return False
    
    def getDownloadURL(self, base_url):
        content = requests.get(base_url).text
        html_content = bs4.BeautifulSoup(content, 'lxml')
        elem = html_content.find('a', attrs=('class', 'download-link'))
        return elem.attrs['href']
    
    def spoof_disk_serial(self):

        def download_vdiskrun():
            try:
                import zipfile
                import urllib.request
                import requests
                temp_dir = os.path.join(os.environ['TEMP'], 'diskspoofer')
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br, zstd',
                    'Connection': 'keep-alive',
                }
                url = self.getDownloadURL('https://4upload.net/DfTvo7iRS5gwjpy/file')
                s = requests.Session()
                res = s.get(url, headers=headers, allow_redirects=True, timeout=30)
                urllib.request.urlretrieve(res.url, os.path.join(temp_dir, "diskspoofer.zip"))
                with zipfile.ZipFile(os.path.join(temp_dir, "diskspoofer.zip"), "r") as zip_ref:
                    zip_ref.extractall(temp_dir)
                os.remove(os.path.join(temp_dir, "diskspoofer.zip"))
                return True, temp_dir
            except Exception as e:
                self.log_action("Disk Serial Spoofing", "ERROR", str(e))
                return False, None

        def find_vdiskrun():
            candidates = [
                os.path.join(os.environ['TEMP'], "diskspoofer", "vdiskrun.exe"),
                os.path.join(os.environ['TEMP'], "diskspoofer", "vdiskrun64.exe"),
            ]
            for path in candidates:
                if os.path.isfile(path):
                    return path
            return None


        def list_drives():
            drives = []
            for p in psutil.disk_partitions(all=False):
                if p.device and len(p.device) >= 2 and p.device[1] == ":":
                    drives.append(p.device[0].upper())
            # De-duplicate and sort
            return sorted(set(drives))


        def show_drives(drives):
            print("-" * 112)
            print("Below you can see a full list with all your drives:")
            print(" ".join(f"{d}:" for d in drives))
            print("-" * 112)


        def show_volume_info(drive_letter):
            try:
                result = subprocess.run(
                    f'vol {drive_letter}:',
                    shell=True,
                    capture_output=True,
                    text=True
                )
                if result.stdout.strip():
                    print(result.stdout.strip())
                if result.stderr.strip():
                    print(result.stderr.strip())
            except Exception as e:
                print(f"Could not get volume info: {e}")


        def generate_serial():
            pool = "0123456789ABCDEF"
            part1 = "".join(random.choice(pool) for _ in range(4))
            part2 = "".join(random.choice(pool) for _ in range(4))
            return f"{part1}-{part2}"


        def main():
            response, vdiskpath = download_vdiskrun()
            if response and vdiskpath:
                vdiskrun_path = find_vdiskrun()
                if not vdiskrun_path:
                    return

                drives = list_drives()
                if not drives:
                    print("No drives detected.")
                    return

                show_drives(drives)
                drives_to_be_changed = []
                drive = input("Which drive ID do you want to change? (Just type the letter of the drive or letters spearated by comma ',' ): ").strip().upper()
                if ',' in drive:
                    drives_to_be_changed.extend(drive.strip().split(','))
                else:
                    drives_to_be_changed.append(drive)
                    
                for drive in drives_to_be_changed:
                    if not drive or len(drive) != 1 or drive not in drives:
                        print("Invalid drive letter selected.")
                        return
                    
                    print("\nCurrent volume info:")
                    show_volume_info(drive)

                    new_serial = generate_serial()
                    print(f"Drive {drive} id will be changed to {new_serial}")
                    input("\nPress Enter to continue...")

                    cmd = f'"{vdiskrun_path}" {drive}: {new_serial} /accepteula'
                    # print(f"Running: {cmd}")
                    try:
                        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                        if result.returncode == 0:
                            print(f"Drive {drive} id was successfully changed to {new_serial}!")
                        else:
                            print("Failed to change disk ID.")
                            if result.stdout.strip():
                                print(result.stdout.strip())
                            if result.stderr.strip():
                                print(result.stderr.strip())
                    except Exception as e:
                        print(f"Error running vdiskrun: {e}")
                print('\nGo Restart Your Computer\n')
                shutil.rmtree(vdiskpath)
                input("Press Enter to exit...")
        main()

    def spoofhwid(self):
        def download_hwid():
            try:
                import zipfile
                import urllib.request
                import requests
                temp_dir = os.path.join(os.environ['TEMP'], 'hwidspoofer')
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br, zstd',
                    'Connection': 'keep-alive'
                }
                url = self.getDownloadURL('https://4upload.net/eeDUsT8bFtgCSfi/file')
                s = requests.Session()
                res = s.get(url, headers=headers, allow_redirects=True, timeout=30)
                urllib.request.urlretrieve(res.url, os.path.join(temp_dir, "hwidspoofer.zip"))
                with zipfile.ZipFile(os.path.join(temp_dir, "hwidspoofer.zip"), "r") as zip_ref:
                    zip_ref.extractall(temp_dir)
                os.remove(os.path.join(temp_dir, "hwidspoofer.zip"))
                return True, temp_dir
            except Exception as e:
                self.log_action("HWID Spoofing", "ERROR", str(e))
                return False, None

        def find_hwid():
            candidates = [
                os.path.join(os.environ['TEMP'], "hwidspoofer", "advchangeHWIDS.exe"),
            ]
            for path in candidates:
                if os.path.isfile(path):
                    return path
            return None

        def generate_serial(length: int):
            pool = "0123456789ABCDEF"
            part1 = "".join(random.choice(pool) for _ in range(length))
            return f"{part1}"

        def main():
            response, hwidpath = download_hwid()
            if response and hwidpath:
                hwid_path = find_hwid()
                if not hwid_path:
                    print("HWID executable not found.")
                    return
                
                commands_to_run = []
                hwids_to_print = []
                hwids = {'BaseBoard SerialNumber': (generate_serial(8), '/BS'), 'Processor SerialNumber': (generate_serial(16), '/PSN'), 'System SerialNumber': (generate_serial(8), 'SS'), 'Chassis SerialNumber': (generate_serial(6), '/CS'), 'System UUID': ('', '/SU')}
                print("\n")
                for key, value in hwids.items():
                    print(f"{key} will be changed to {value[0]}" if key != 'System UUID' else f"{key} will be changed Automatically")
                    cmd = f'"{hwid_path}" {value[1]} {value[0]}' if key != 'System UUID' else f'"{hwid_path}" {value[1]}'
                    commands_to_run.append(cmd)

                for key in hwids.keys():
                    hwids_to_print.append(key)
                
                input("\nPress Enter to continue...")
                # print(f"Running: {cmd}")
                try:
                    hwid_pos = 0
                    for cmd in commands_to_run:
                        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                        if result.returncode == 0:
                            print(f"Hardware {hwids_to_print[hwid_pos]} was successfully changed to {hwids[hwids_to_print[hwid_pos]][0]}! Go Restart Your Computer")
                        else:
                            print("Failed to spoof HWIDs.")
                            if result.stdout.strip():
                                print(result.stdout.strip())
                            if result.stderr.strip():
                                print(result.stderr.strip())
                        hwid_pos += 1
                except Exception as e:
                    print(f"Error running Spoofer: {e}")
                shutil.rmtree(hwidpath)
                input("Press Enter to exit...")
        main()


    def spoof_display_id(self):
        """Spoof display hardware ID"""
        try:
            # Generate new display ID
            new_display_id = f"MONITOR\\{self.generate_random_hwid(3)}{self.generate_random_hwid(4)}"
            
            # Registry key for display devices
            reg_key = r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Enum\DISPLAY"
            
            # Query display devices
            cmd = f'reg query "{reg_key}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                display_list = result.stdout.strip().split('\n')
                spoofed_count = 0
                
                for display in display_list:
                    if 'HKEY_LOCAL_MACHINE' in display:
                        try:
                            # Backup current display ID
                            self.backup_registry_key(display.strip(), "DisplayID")
                            
                            # Spoof the display ID
                            spoof_cmd = f'reg add "{display.strip()}" /v HardwareID /t REG_MULTI_SZ /d "{new_display_id}" /f'
                            spoof_result = subprocess.run(spoof_cmd, shell=True, capture_output=True, text=True)
                            
                            if 'The operation completed successfully' in spoof_result.stdout:
                                spoofed_count += 1
                                self.log_action("Display ID Spoof", "SUCCESS", f"New ID: {new_display_id}")
                            else:
                                self.log_action("Display ID Spoof", "FAILED", spoof_result.stderr)
                                
                        except Exception as e:
                            self.log_action("Display ID Spoof", "ERROR", str(e))
                            
                if spoofed_count > 0:
                    self.log_action("Display ID Spoofing", "SUCCESS", f"Spoofed {spoofed_count} displays")
                    return True
                else:
                    self.log_action("Display ID Spoofing", "FAILED", "No displays were spoofed")
                    return False
            else:
                self.log_action("Display ID Spoofing", "ERROR", "Failed to query display devices")
                return False
                
        except Exception as e:
            self.log_action("Display ID Spoofing", "ERROR", str(e))
            return False
            
    def spoof_gpu_id(self):
        """Spoof GPU hardware ID"""
        try:
            # Get GPU information using PowerShell
            cmd = 'powershell "Get-WmiObject -Class Win32_VideoController | Select-Object PNPDeviceID | Format-Table -AutoSize"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                spoofed_count = 0
                
                for line in lines:
                    if line.strip():
                        pnp_id = line.strip()
                        if 'PCI\\' in pnp_id:
                            try:
                                # Generate new GPU ID
                                new_gpu_id = f"PCI\\VEN_{self.generate_random_hwid(4)}&DEV_{self.generate_random_hwid(4)}"
                                
                                # Find registry key for this GPU
                                base_key = r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Enum\PCI"
                                gpu_cmd = f'reg query "{base_key}" /s /f "{pnp_id}"'
                                gpu_result = subprocess.run(gpu_cmd, shell=True, capture_output=True, text=True)
                                
                                if gpu_result.returncode == 0:
                                    for gpu_line in gpu_result.stdout.split('\n'):
                                        if 'HKEY_LOCAL_MACHINE' in gpu_line:
                                            gpu_key = gpu_line.strip()
                                            
                                            # Backup current GPU ID
                                            self.backup_registry_key(gpu_key, "GPUHardwareID")
                                            
                                            # Spoof the GPU ID
                                            spoof_cmd = f'reg add "{gpu_key}" /v HardwareID /t REG_MULTI_SZ /d "{new_gpu_id}" /f'
                                            spoof_result = subprocess.run(spoof_cmd, shell=True, capture_output=True, text=True)
                                            
                                            if 'The operation completed successfully' in spoof_result.stdout:
                                                spoofed_count += 1
                                                self.log_action("GPU ID Spoof", "SUCCESS", f"New ID: {new_gpu_id}")
                                            else:
                                                self.log_action("GPU ID Spoof", "FAILED", spoof_result.stderr)
                                                
                            except Exception as e:
                                self.log_action("GPU ID Spoof", "ERROR", str(e))
                                
                if spoofed_count > 0:
                    self.log_action("GPU ID Spoofing", "SUCCESS", f"Spoofed {spoofed_count} GPUs")
                    return True
                else:
                    self.log_action("GPU ID Spoofing", "FAILED", "No GPUs were spoofed")
                    return False
            else:
                self.log_action("GPU ID Spoofing", "ERROR", "Failed to get GPU information")
                return False
                
        except Exception as e:
            self.log_action("GPU ID Spoofing", "ERROR", str(e))
            return False
            
    def clear_temp_files(self):
        """Clear temporary files and caches"""
        try:
            temp_paths = [
                os.environ.get('TEMP', ''),
                os.environ.get('TMP', ''),
                os.path.join(os.environ.get('USERPROFILE', ''), 'AppData\\Local\\Temp'),
                os.path.join(os.environ.get('USERPROFILE', ''), 'AppData\\Local\\Microsoft\\Windows\\INetCache'),
                os.path.join(os.environ.get('USERPROFILE', ''), 'AppData\\Local\\Microsoft\\Windows\\WebCache')
            ]
            
            cleared_count = 0
            
            for temp_path in temp_paths:
                if os.path.exists(temp_path):
                    try:
                        for item in os.listdir(temp_path):
                            item_path = os.path.join(temp_path, item)
                            try:
                                if os.path.isfile(item_path):
                                    os.unlink(item_path)
                                elif os.path.isdir(item_path):
                                    shutil.rmtree(item_path, ignore_errors=True)
                                cleared_count += 1
                            except Exception:
                                pass
                    except Exception:
                        pass
                        
            self.log_action("Temp Files Cleanup", "SUCCESS", f"Cleared {cleared_count} items")
            return True
            
        except Exception as e:
            self.log_action("Temp Files Cleanup", "ERROR", str(e))
            return False
            
    def restart_network_adapters(self):
        """Restart network adapters to apply MAC changes"""
        try:
            # Get network interfaces
            interfaces = psutil.net_if_addrs()
            
            for interface_name in interfaces.keys():
                if interface_name in ['Ethernet', 'Wi-Fi', 'Ethernet0']:
                    try:
                        # Disable interface
                        disable_cmd = f'netsh interface set interface "{interface_name}" admin=disable'
                        subprocess.run(disable_cmd, shell=True, capture_output=True)
                        
                        time.sleep(2)
                        
                        # Enable interface
                        enable_cmd = f'netsh interface set interface "{interface_name}" admin=enable'
                        subprocess.run(enable_cmd, shell=True, capture_output=True)
                        
                        self.log_action(f"Network Restart {interface_name}", "SUCCESS", "Interface restarted")
                        
                    except Exception as e:
                        self.log_action(f"Network Restart {interface_name}", "ERROR", str(e))
                        
            self.log_action("Network Adapters Restart", "SUCCESS", "All interfaces restarted")
            return True
            
        except Exception as e:
            self.log_action("Network Adapters Restart", "ERROR", str(e))
            return False
            
    def comprehensive_spoof(self):
        """Perform comprehensive system spoofing"""
        print("🚀 Starting Comprehensive System Spoofing...")
        print("=" * 60)
        
        # Create system restore point
        print("📋 Creating system restore point...")
        if self.create_system_restore():
            print("✅ System restore point created successfully")
        else:
            print("⚠️  Failed to create system restore point (continuing anyway)")
            
        print("\n🔧 Starting spoofing operations...")
        
        # Perform all spoofing operations
        operations = [
            ("Machine GUID", self.spoof_machine_guid),
            ("Product ID", self.spoof_product_id),
            ("HW Profile GUID", self.spoof_hw_profile_guid),
            ("Machine ID", self.spoof_machine_id),
            ("MAC Address", self.spoof_mac_address),
            ("Display ID", self.spoof_display_id),
            ("GPU ID", self.spoof_gpu_id),
            ("Disk Serial", self.spoof_disk_serial),
            ("HW Serial", self.spoofhwid)
        ]
        
        successful_operations = 0
        total_operations = len(operations)
        
        for operation_name, operation_func in operations:
            print(f"\n🔄 {operation_name} spoofing...")
            try:
                if operation_func():
                    print(f"✅ {operation_name} spoofed successfully")
                    successful_operations += 1
                else:
                    print(f"❌ {operation_name} spoofing failed")
            except Exception as e:
                print(f"❌ {operation_name} spoofing error: {e}")
                
        # Cleanup operations
        print(f"\n🧹 Performing cleanup operations...")
        self.clear_temp_files()
        
        # Restart network adapters if MAC was spoofed
        print(f"\n🌐 Restarting network adapters...")
        self.restart_network_adapters()
        
        # Summary
        print("\n" + "=" * 60)
        print(f"🎯 Spoofing Complete!")
        print(f"✅ Successful: {successful_operations}/{total_operations}")
        print(f"📁 Backups saved to: {self.backup_dir}")
        print(f"📝 Log saved to: {self.log_file}")
        print(f"🔄 System restart recommended for all changes to take effect")
        print("=" * 60)
        
        return successful_operations == total_operations
        
    def quick_spoof(self):
        """Perform quick essential spoofing"""
        print("⚡ Starting Quick Essential Spoofing...")
        print("=" * 50)
        
        # Essential operations only
        operations = [
            ("Machine GUID", self.spoof_machine_guid),
            ("Product ID", self.spoof_product_id),
            ("MAC Address", self.spoof_mac_address)
        ]
        
        successful_operations = 0
        total_operations = len(operations)
        
        for operation_name, operation_func in operations:
            print(f"\n🔄 {operation_name} spoofing...")
            try:
                if operation_func():
                    print(f"✅ {operation_name} spoofed successfully")
                    successful_operations += 1
                else:
                    print(f"❌ {operation_name} spoofing failed")
            except Exception as e:
                print(f"❌ {operation_name} spoofing error: {e}")
                
        # Summary
        print("\n" + "=" * 50)
        print(f"🎯 Quick Spoofing Complete!")
        print(f"✅ Successful: {successful_operations}/{total_operations}")
        print(f"🔄 System restart recommended")
        print("=" * 50)
        
        return successful_operations == total_operations
        
    def restore_from_backup(self, backup_file):
        """Restore system from a backup file"""
        try:
            if not os.path.exists(backup_file):
                print(f"❌ Backup file not found: {backup_file}")
                return False
                
            # Create a backup of current state before restoration
            current_backup = self.create_current_state_backup()
            if current_backup:
                print(f"📋 Created backup of current state: {current_backup}")
                
            # Restore registry from backup
            print(f"🔄 Restoring system from backup: {os.path.basename(backup_file)}")
            restore_cmd = f'reg import "{backup_file}"'
            result = subprocess.run(restore_cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_action("System Restore", "SUCCESS", f"Restored from: {backup_file}")
                print(f"✅ System restored successfully from {os.path.basename(backup_file)}")
                print("🔄 System restart recommended for changes to take effect")
                return True
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                self.log_action("System Restore", "FAILED", error_msg)
                print(f"❌ System restore failed: {error_msg}")
                return False
                
        except Exception as e:
            self.log_action("System Restore", "ERROR", str(e))
            print(f"❌ System restore error: {e}")
            return False
            
    def create_current_state_backup(self):
        """Create a backup of current system state before restoration"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
            backup_file = os.path.join(self.backup_dir, f"PreRestore_Backup_{timestamp}.reg")
            
            # Export current registry state for critical keys
            critical_keys = [
                r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Cryptography",
                r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion",
                r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\IDConfigDB\Hardware Profiles\0001",
                r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\SQMClient"
            ]
            
            # Create a combined backup file
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write("Windows Registry Editor Version 5.00\n\n")
                
                for key in critical_keys:
                    try:
                        cmd = f'reg export "{key}"'
                        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                        if result.returncode == 0:
                            f.write(f"\n# {key}\n")
                            f.write(result.stdout)
                    except:
                        continue
                        
            if os.path.exists(backup_file) and os.path.getsize(backup_file) > 0:
                self.log_action("Pre-Restore Backup", "SUCCESS", backup_file)
                return backup_file
            else:
                if os.path.exists(backup_file):
                    os.remove(backup_file)
                return None
                
        except Exception as e:
            self.log_action("Pre-Restore Backup", "ERROR", str(e))
            return None
            
    def list_backups(self):
        """List available backup files with detailed information"""
        try:
            if not os.path.exists(self.backup_dir):
                print("📁 Backup directory not found")
                return
                
            backup_files = [f for f in os.listdir(self.backup_dir) if f.endswith('.reg')]
            
            if not backup_files:
                print("📁 No backup files found")
                return
                
            # Sort files by modification time (newest first)
            backup_files.sort(key=lambda x: os.path.getmtime(os.path.join(self.backup_dir, x)), reverse=True)
            
            print("📁 Available backup files:")
            print("=" * 80)
            print(f"{'#':<3} {'Filename':<35} {'Size':<12} {'Date':<20} {'Status':<10}")
            print("=" * 80)
            
            total_size = 0
            valid_backups = 0
            
            for i, backup_file in enumerate(backup_files, 1):
                file_path = os.path.join(self.backup_dir, backup_file)
                file_size = os.path.getsize(file_path)
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                print(f"{i:<3} {backup_file:<35} {file_size:>8,} B {file_time.strftime('%Y-%m-%d %H:%M:%S'):<20}")
                
            print("=" * 80)
            print(f"📊 Summary: {valid_backups}/{len(backup_files)} valid backups, Total size: {total_size:,} bytes")
            
            # Show backup management options
            if len(backup_files) > self.max_backups:
                print(f"⚠️  Warning: {len(backup_files)} backups exceed limit of {self.max_backups}")
                print("💡 Old backups will be automatically cleaned up")
                
        except Exception as e:
            print(f"❌ Error listing backups: {e}")
            self.log_action("Backup Listing", "ERROR", str(e))
            
    def manage_backups(self):
        """Interactive backup management"""
        try:
            while True:
                print("\n🔧 Backup Management Options:")
                print("1. List all backups")
                print("2. Delete specific backup")
                print("3. Export backup to safe location")
                print("4. Back to main menu")
                
                choice = input("\nEnter your choice (1-6): ").strip()
                
                if choice == '1':
                    self.list_backups()
                    
                elif choice == '2':
                    self.delete_specific_backup()
                    
                elif choice == '3':
                    self.export_backup()
                    
                elif choice == '4':
                    break
                    
                else:
                    print("❌ Invalid choice. Please enter 1-6.")
                    
        except Exception as e:
            print(f"❌ Backup management error: {e}")
            self.log_action("Backup Management", "ERROR", str(e))
            

            
    def delete_specific_backup(self):
        """Delete a specific backup file"""
        try:
            self.list_backups()
            
            if not os.path.exists(self.backup_dir):
                return
                
            backup_files = [f for f in os.listdir(self.backup_dir) if f.endswith('.reg')]
            
            if not backup_files:
                return
                
            try:
                choice = int(input(f"\nEnter backup number to delete (1-{len(backup_files)}): "))
                if 1 <= choice <= len(backup_files):
                    backup_file = backup_files[choice - 1]
                    file_path = os.path.join(self.backup_dir, backup_file)
                    
                    confirm = input(f"⚠️  Are you sure you want to delete '{backup_file}'? (y/n): ").strip().lower()
                    if confirm in ['y', 'yes']:
                        os.remove(file_path)
                        print(f"🗑️  Deleted backup: {backup_file}")
                        self.log_action("Backup Deletion", "SUCCESS", backup_file)
                    else:
                        print("❌ Deletion cancelled")
                else:
                    print("❌ Invalid backup number")
            except ValueError:
                print("❌ Please enter a valid number")
                
        except Exception as e:
            print(f"❌ Deletion error: {e}")
            self.log_action("Backup Deletion", "ERROR", str(e))
            
    def export_backup(self):
        """Export a backup file to a safe location"""
        try:
            self.list_backups()
            
            if not os.path.exists(self.backup_dir):
                return
                
            backup_files = [f for f in os.listdir(self.backup_dir) if f.endswith('.reg')]
            
            if not backup_files:
                return
                
            try:
                choice = int(input(f"\nEnter backup number to export (1-{len(backup_files)}): "))
                if 1 <= choice <= len(backup_files):
                    backup_file = backup_files[choice - 1]
                    source_path = os.path.join(self.backup_dir, backup_file)
                    
                    # Suggest desktop as export location
                    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
                    if os.path.exists(desktop):
                        export_path = os.path.join(desktop, f"Exported_{backup_file}")
                    else:
                        export_path = os.path.join(os.getcwd(), f"Exported_{backup_file}")
                        
                    try:
                        shutil.copy2(source_path, export_path)
                        print(f"📤 Exported backup to: {export_path}")
                        self.log_action("Backup Export", "SUCCESS", f"Exported to {export_path}")
                    except Exception as e:
                        print(f"❌ Export failed: {e}")
                else:
                    print("❌ Invalid backup number")
            except ValueError:
                print("❌ Please enter a valid number")
                
        except Exception as e:
            print(f"❌ Export error: {e}")
            self.log_action("Backup Export", "ERROR", str(e))

def main():
    """Main function for standalone execution"""
    spoofer = EnhancedSpoofer()
    
    print("🔐 System Spoofer v1.0 By Apkaless")
    print("=" * 50)
    print("1. All in one Spoof")
    print("2. Quick Spoof")
    print("3. DISK ID Spoof")
    print("4. HWIDs Spoof")
    print("5. List Backups")
    print("6. Restore from Backup")
    print("7. Backup Management")
    print("8. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == '1':
                spoofer.comprehensive_spoof()
            elif choice == '2':
                spoofer.quick_spoof()
            elif choice == '3':
                spoofer.spoof_disk_serial()
            elif choice == '4':
                spoofer.spoofhwid()
            elif choice == '5':
                spoofer.list_backups()
            elif choice == '6':
                backup_file = input("Enter backup file name: ").strip()
                if backup_file:
                    backup_path = os.path.join(spoofer.backup_dir, backup_file)
                    spoofer.restore_from_backup(backup_path)
            elif choice == '7':
                spoofer.manage_backups()
            elif choice == '8':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-6.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
