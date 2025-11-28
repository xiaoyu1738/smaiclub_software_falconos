# src/falcon/core/updater.py
import requests
import os
import sys
import subprocess
from tqdm import tqdm
try:
    from PyQt6.QtWidgets import QMessageBox, QProgressDialog
    from PyQt6.QtCore import Qt
    HAS_QT = True
except ImportError:
    HAS_QT = False

# --- Config ---
REPO_OWNER = "xiaoyu1738"
REPO_NAME = "smaiclub_software_falconos"
API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"

def _parse_version(version_str):
    """
    Robustly parses version string, ignoring non-digit suffixes.
    '2.5.0 GUI' -> (2, 5, 0)
    """
    clean_version_str = "".join(filter(lambda x: x.isdigit() or x == '.', version_str.split()[0]))
    try:
        return tuple(map(int, clean_version_str.split('.')))
    except (ValueError, IndexError):
        return (0, 0, 0)

def _apply_update_and_restart(new_exe_path):
    """Creates and executes a batch script to replace old file and restart (Windows only)."""
    if os.name != 'nt':
        print("Auto-update only supported on Windows. Please replace files manually.")
        return

    current_exe_path = sys.executable
    batch_script = f"""
@echo off
echo Updating FALCON OS... Please wait.
timeout /t 3 /nobreak > NUL
taskkill /F /IM "{os.path.basename(current_exe_path)}" > NUL
del "{current_exe_path}"
echo Old version removed. Starting new version...
start "" "{new_exe_path}"
(goto) 2>nul & del "%~f0"
"""
    updater_path = os.path.join(os.getcwd(), "updater.bat")
    with open(updater_path, "w") as f:
        f.write(batch_script)

    subprocess.Popen(updater_path, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
    sys.exit()

def download_asset(asset_data, parent_widget=None):
    """Downloads the specified asset file."""
    download_url = asset_data.get("browser_download_url")
    filename = asset_data.get("name")

    try:
        print(f"Downloading: {filename}...")
        response = requests.get(download_url, stream=True, timeout=10)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))

        if parent_widget and HAS_QT:  # GUI mode
            progress_dialog = QProgressDialog(f"Downloading {filename}...", "Cancel", 0, total_size, parent_widget)
            progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
            progress_dialog.setValue(0)

            with open(filename, 'wb') as f:
                downloaded_size = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if progress_dialog.wasCanceled():
                        return None
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    progress_dialog.setValue(downloaded_size)
            return os.path.abspath(filename)

        else:  # CLI mode
            with open(filename, 'wb') as f, tqdm(
                    desc=f"Downloading", total=total_size, unit='B',
                    unit_scale=True, unit_divisor=1024
            ) as bar:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    bar.update(len(chunk))
            return os.path.abspath(filename)

    except Exception as e:
        print(f"Download error: {e}")
        if parent_widget and HAS_QT:
            QMessageBox.critical(parent_widget, "Download Error", f"Error downloading update: {e}")
        return None

def check_for_updates(current_version, target_asset_keyword, parent_widget=None, silent=False):
    """
    Check GitHub Releases for updates.
    """
    if not silent:
        if parent_widget and HAS_QT:
            QMessageBox.information(parent_widget, "Check for Updates", "Connecting to GitHub...")
        else:
            print("Connecting to GitHub to check for updates...")

    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        latest_release = response.json()
        latest_tag = latest_release.get("tag_name", "0.0.0")
        latest_version_str = latest_tag.lstrip('v')

        current_version_tuple = _parse_version(current_version)
        latest_version_tuple = _parse_version(latest_version_str)

        if latest_version_tuple > current_version_tuple:
            message = (
                f"New version found!\n\n"
                f"Current: {current_version}\n"
                f"Latest: {latest_version_str}\n\n"
                f"Download and update now?"
            )

            if parent_widget and HAS_QT:
                reply = QMessageBox.question(parent_widget, "New Version Found", message,
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    asset_to_download = next((asset for asset in latest_release.get("assets", [])
                                              if target_asset_keyword in asset.get("name", "").lower()), None)
                    if asset_to_download:
                        new_exe_path = download_asset(asset_to_download, parent_widget)
                        if new_exe_path:
                            _apply_update_and_restart(new_exe_path)
                    else:
                        QMessageBox.warning(parent_widget, "Error", f"Asset containing '{target_asset_keyword}' not found.")
            else: # CLI Mode
                print("\n" + "="*60)
                print(f"New version found! (Current: {current_version}, Latest: {latest_version_str})")
                print("="*60 + "\n")
                choice = input("Download and update now? (y/n): ").lower()
                if choice == 'y':
                    asset_to_download = next((asset for asset in latest_release.get("assets", [])
                                              if target_asset_keyword in asset.get("name", "").lower()), None)
                    if asset_to_download:
                        new_exe_path = download_asset(asset_to_download)
                        if new_exe_path:
                            _apply_update_and_restart(new_exe_path)
                    else:
                        print(f"Error: Asset containing '{target_asset_keyword}' not found.")
        else:
            if not silent:
                if parent_widget and HAS_QT:
                    QMessageBox.information(parent_widget, "Up to Date", f"You are using the latest version ({current_version}).")
                else:
                    print("You are using the latest version.")

    except requests.exceptions.RequestException as e:
        if not silent:
            error_message = f"Update check failed: Connection error.\n\nError: {e}"
            if parent_widget and HAS_QT:
                QMessageBox.warning(parent_widget, "Network Error", error_message)
            else:
                print(error_message)
    except Exception as e:
        if not silent:
            error_message = f"Unknown error during update check: {e}"
            if parent_widget and HAS_QT:
                QMessageBox.critical(parent_widget, "Update Error", error_message)
            else:
                print(error_message)
