import os
import shutil
import subprocess
import time
import psutil
import winreg
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import glob

@dataclass
class CleanResult:
    success: bool
    message: str
    items_cleaned: int = 0
    space_freed: int = 0  # in bytes

class SystemCleaner:
    """Advanced Windows System Cleaner with comprehensive cleanup options"""
    
    def __init__(self):
        self.temp_paths = [
            os.environ.get('TEMP', ''),
            os.environ.get('TMP', ''),
            os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Local', 'Temp'),
            os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Local', 'Microsoft', 'Windows', 'INetCache'),
            os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Local', 'Microsoft', 'Windows', 'WebCache'),
            os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Local', 'Microsoft', 'Windows', 'History'),
            os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Local', 'Microsoft', 'Windows', 'Temporary Internet Files'),
            os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Local', 'Microsoft', 'Edge', 'User Data', 'Default', 'Cache'),
            os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Cache'),
            os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Local', 'Mozilla', 'Firefox', 'Profiles'),
            os.path.join(os.environ.get('WINDIR', ''), 'Temp'),
            os.path.join(os.environ.get('WINDIR', ''), 'Prefetch'),
            os.path.join(os.environ.get('WINDIR', ''), 'SoftwareDistribution', 'Download'),
        ]
        
        self.log_paths = [
            os.path.join(os.environ.get('WINDIR', ''), 'Logs'),
            os.path.join(os.environ.get('WINDIR', ''), 'Panther'),
            os.path.join(os.environ.get('WINDIR', ''), 'System32', 'LogFiles'),
            os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Local', 'Microsoft', 'Windows', 'Explorer'),
        ]
        
        self.cache_paths = [
            os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Local', 'Microsoft', 'Windows', 'Caches'),
            os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Roaming', 'Microsoft', 'Windows', 'Recent'),
            os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Local', 'Microsoft', 'Windows', 'Recent'),
        ]

    def _is_admin(self) -> bool:
        """Check if running as administrator"""
        try:
            import ctypes
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            return False

    def _get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        try:
            return os.path.getsize(file_path)
        except Exception:
            return 0

    def _get_folder_size(self, folder_path: str) -> int:
        """Get total size of folder in bytes"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(folder_path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    total_size += self._get_file_size(file_path)
        except Exception:
            pass
        return total_size

    def _safe_remove(self, path: str) -> Tuple[bool, int]:
        """Safely remove file or directory, return (success, size_freed)"""
        try:
            if os.path.isfile(path):
                size = self._get_file_size(path)
                os.unlink(path)
                return True, size
            elif os.path.isdir(path):
                size = self._get_folder_size(path)
                shutil.rmtree(path, ignore_errors=True)
                return True, size
        except Exception:
            pass
        return False, 0

    def _format_size(self, size_bytes: int) -> str:
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"

    def clean_temp_files(self) -> CleanResult:
        """Clean temporary files from various locations"""
        total_items = 0
        total_size = 0
        
        for temp_path in self.temp_paths:
            if not temp_path or not os.path.exists(temp_path):
                continue
                
            try:
                for item in os.listdir(temp_path):
                    item_path = os.path.join(temp_path, item)
                    success, size = self._safe_remove(item_path)
                    if success:
                        total_items += 1
                        total_size += size
            except Exception:
                continue
        
        return CleanResult(
            True, 
            f"Cleaned {total_items} temporary items ({self._format_size(total_size)})",
            total_items,
            total_size
        )

    def clean_browser_cache(self) -> CleanResult:
        """Clean browser caches"""
        browser_paths = [
            # Chrome
            os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Cache'),
            os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Code Cache'),
            # Edge
            os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Local', 'Microsoft', 'Edge', 'User Data', 'Default', 'Cache'),
            os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Local', 'Microsoft', 'Edge', 'User Data', 'Default', 'Code Cache'),
            # Firefox
            os.path.join(os.environ.get('USERPROFILE', ''), 'AppData', 'Local', 'Mozilla', 'Firefox', 'Profiles'),
        ]
        
        total_items = 0
        total_size = 0
        
        for browser_path in browser_paths:
            if not os.path.exists(browser_path):
                continue
                
            try:
                if 'Firefox' in browser_path:
                    # Firefox has multiple profiles
                    for profile_dir in os.listdir(browser_path):
                        profile_path = os.path.join(browser_path, profile_dir)
                        if os.path.isdir(profile_path):
                            cache_path = os.path.join(profile_path, 'cache2')
                            if os.path.exists(cache_path):
                                success, size = self._safe_remove(cache_path)
                                if success:
                                    total_items += 1
                                    total_size += size
                else:
                    # Chrome/Edge cache directories
                    for cache_dir in ['Cache', 'Code Cache', 'GPUCache']:
                        cache_path = os.path.join(browser_path, cache_dir)
                        if os.path.exists(cache_path):
                            success, size = self._safe_remove(cache_path)
                            if success:
                                total_items += 1
                                total_size += size
            except Exception:
                continue
        
        return CleanResult(
            True,
            f"Cleaned browser cache: {total_items} items ({self._format_size(total_size)})",
            total_items,
            total_size
        )

    def clean_system_logs(self) -> CleanResult:
        """Clean system log files"""
        total_items = 0
        total_size = 0
        
        for log_path in self.log_paths:
            if not os.path.exists(log_path):
                continue
                
            try:
                for item in os.listdir(log_path):
                    item_path = os.path.join(log_path, item)
                    # Only clean .log files older than 7 days
                    if item.endswith('.log') and os.path.isfile(item_path):
                        file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(item_path))
                        if file_age > timedelta(days=7):
                            success, size = self._safe_remove(item_path)
                            if success:
                                total_items += 1
                                total_size += size
            except Exception:
                continue
        
        return CleanResult(
            True,
            f"Cleaned {total_items} old log files ({self._format_size(total_size)})",
            total_items,
            total_size
        )

    def clean_windows_update_cache(self) -> CleanResult:
        """Clean Windows Update cache"""
        if not self._is_admin():
            return CleanResult(False, "Administrator privileges required for Windows Update cache cleanup")
        
        update_paths = [
            os.path.join(os.environ.get('WINDIR', ''), 'SoftwareDistribution', 'Download'),
            os.path.join(os.environ.get('WINDIR', ''), 'SoftwareDistribution', 'DataStore'),
        ]
        
        total_items = 0
        total_size = 0
        
        for update_path in update_paths:
            if not os.path.exists(update_path):
                continue
                
            try:
                for item in os.listdir(update_path):
                    item_path = os.path.join(update_path, item)
                    success, size = self._safe_remove(item_path)
                    if success:
                        total_items += 1
                        total_size += size
            except Exception:
                continue
        
        return CleanResult(
            True,
            f"Cleaned Windows Update cache: {total_items} items ({self._format_size(total_size)})",
            total_items,
            total_size
        )

    def clean_recycle_bin(self) -> CleanResult:
        """Empty the Recycle Bin"""
        try:
            # Use PowerShell to empty recycle bin
            cmd = 'powershell.exe -Command "Clear-RecycleBin -Force"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                return CleanResult(True, "Recycle Bin emptied successfully")
            else:
                return CleanResult(False, f"Failed to empty Recycle Bin: {result.stderr}")
        except Exception as e:
            return CleanResult(False, f"Recycle Bin cleanup failed: {e}")

    def clean_prefetch_files(self) -> CleanResult:
        """Clean Windows Prefetch files"""
        if not self._is_admin():
            return CleanResult(False, "Administrator privileges required for Prefetch cleanup")
        
        prefetch_path = os.path.join(os.environ.get('WINDIR', ''), 'Prefetch')
        if not os.path.exists(prefetch_path):
            return CleanResult(False, "Prefetch directory not found")
        
        total_items = 0
        total_size = 0
        
        try:
            for item in os.listdir(prefetch_path):
                if item.endswith('.pf'):
                    item_path = os.path.join(prefetch_path, item)
                    success, size = self._safe_remove(item_path)
                    if success:
                        total_items += 1
                        total_size += size
        except Exception as e:
            return CleanResult(False, f"Prefetch cleanup failed: {e}")
        
        return CleanResult(
            True,
            f"Cleaned {total_items} Prefetch files ({self._format_size(total_size)})",
            total_items,
            total_size
        )

    def clean_recent_files(self) -> CleanResult:
        """Clean recent files history"""
        total_items = 0
        total_size = 0
        
        for cache_path in self.cache_paths:
            if not os.path.exists(cache_path):
                continue
                
            try:
                for item in os.listdir(cache_path):
                    item_path = os.path.join(cache_path, item)
                    success, size = self._safe_remove(item_path)
                    if success:
                        total_items += 1
                        total_size += size
            except Exception:
                continue
        
        return CleanResult(
            True,
            f"Cleaned recent files: {total_items} items ({self._format_size(total_size)})",
            total_items,
            total_size
        )

    def clean_disk_cleanup(self) -> CleanResult:
        """Run Windows Disk Cleanup"""
        try:
            cmd = 'cleanmgr /sagerun:1'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                return CleanResult(True, "Disk Cleanup completed successfully")
            else:
                return CleanResult(False, f"Disk Cleanup failed: {result.stderr}")
        except Exception as e:
            return CleanResult(False, f"Disk Cleanup failed: {e}")

    def comprehensive_clean(self) -> List[CleanResult]:
        """Perform comprehensive system cleanup"""
        results = []
        
        print("🧹 Starting comprehensive system cleanup...")
        
        # Clean temporary files
        print("📁 Cleaning temporary files...")
        results.append(self.clean_temp_files())
        
        # Clean browser cache
        print("🌐 Cleaning browser cache...")
        results.append(self.clean_browser_cache())
        
        # Clean system logs
        print("📋 Cleaning system logs...")
        results.append(self.clean_system_logs())
        
        # Clean Windows Update cache (if admin)
        if self._is_admin():
            print("🔄 Cleaning Windows Update cache...")
            results.append(self.clean_windows_update_cache())
        
        # Clean Prefetch files (if admin)
        if self._is_admin():
            print("⚡ Cleaning Prefetch files...")
            results.append(self.clean_prefetch_files())
        
        # Clean recent files
        print("📝 Cleaning recent files...")
        results.append(self.clean_recent_files())
        
        # Empty Recycle Bin
        print("🗑️ Emptying Recycle Bin...")
        results.append(self.clean_recycle_bin())
        
        return results

    def get_system_info(self) -> Dict[str, str]:
        """Get current system information"""
        try:
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_free = self._format_size(disk.free)
            disk_total = self._format_size(disk.total)
            disk_used_percent = (disk.used / disk.total) * 100
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_used_percent = memory.percent
            memory_total = self._format_size(memory.total)
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            return {
                'disk_free': disk_free,
                'disk_total': disk_total,
                'disk_used_percent': f"{disk_used_percent:.1f}%",
                'memory_used_percent': f"{memory_used_percent:.1f}%",
                'memory_total': memory_total,
                'cpu_percent': f"{cpu_percent:.1f}%"
            }
        except Exception as e:
            return {'error': str(e)}

def main():
    """Standalone CLI for System Cleaner"""
    cleaner = SystemCleaner()
    
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("🧹 ADVANCED SYSTEM CLEANER 🧹")
        print("=" * 40)
        print("1. Clean Temporary Files")
        print("2. Clean Browser Cache")
        print("3. Clean System Logs")
        print("4. Clean Windows Update Cache (Admin)")
        print("5. Clean Prefetch Files (Admin)")
        print("6. Clean Recent Files")
        print("7. Empty Recycle Bin")
        print("8. Run Disk Cleanup")
        print("9. Comprehensive Clean")
        print("10. System Information")
        print("0. Exit")
        print("=" * 40)
        
        choice = input("\nSelect option (0-10): ").strip()
        
        if choice == '0':
            print("👋 Goodbye!")
            break
        elif choice == '1':
            result = cleaner.clean_temp_files()
            print(f"\n{'✅' if result.success else '❌'} {result.message}")
        elif choice == '2':
            result = cleaner.clean_browser_cache()
            print(f"\n{'✅' if result.success else '❌'} {result.message}")
        elif choice == '3':
            result = cleaner.clean_system_logs()
            print(f"\n{'✅' if result.success else '❌'} {result.message}")
        elif choice == '4':
            result = cleaner.clean_windows_update_cache()
            print(f"\n{'✅' if result.success else '❌'} {result.message}")
        elif choice == '5':
            result = cleaner.clean_prefetch_files()
            print(f"\n{'✅' if result.success else '❌'} {result.message}")
        elif choice == '6':
            result = cleaner.clean_recent_files()
            print(f"\n{'✅' if result.success else '❌'} {result.message}")
        elif choice == '7':
            result = cleaner.clean_recycle_bin()
            print(f"\n{'✅' if result.success else '❌'} {result.message}")
        elif choice == '8':
            result = cleaner.clean_disk_cleanup()
            print(f"\n{'✅' if result.success else '❌'} {result.message}")
        elif choice == '9':
            results = cleaner.comprehensive_clean()
            print("\n📊 CLEANUP SUMMARY:")
            print("-" * 30)
            total_items = 0
            total_size = 0
            for result in results:
                print(f"{'✅' if result.success else '❌'} {result.message}")
                total_items += result.items_cleaned
                total_size += result.space_freed
            
            print(f"\n🎉 TOTAL: {total_items} items cleaned, {cleaner._format_size(total_size)} freed")
        elif choice == '10':
            info = cleaner.get_system_info()
            print("\n💻 SYSTEM INFORMATION:")
            print("-" * 25)
            for key, value in info.items():
                print(f"{key.replace('_', ' ').title()}: {value}")
        else:
            print("❌ Invalid option!")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
