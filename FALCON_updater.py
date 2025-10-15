# FALCON_updater.py
import requests
import os
import sys
import subprocess
import time
from tqdm import tqdm
from PyQt6.QtWidgets import QMessageBox, QProgressDialog
from PyQt6.QtCore import Qt

# --- 配置 ---
REPO_OWNER = "xiaoyu1738"
REPO_NAME = "smaiclub_software_falconos"
API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"


def _parse_version(version_str):
    """
    健壮地解析版本字符串，忽略任何非数字后缀（如 ' GUI'）。
    '2.5.0 GUI' -> (2, 5, 0)
    '2.3.1' -> (2, 3, 1)
    """
    # 移除所有非数字和非点号的字符
    clean_version_str = "".join(filter(lambda x: x.isdigit() or x == '.', version_str.split()[0]))
    try:
        return tuple(map(int, clean_version_str.split('.')))
    except (ValueError, IndexError):
        # 如果解析失败，返回一个很低的版本号
        return (0, 0, 0)


def _apply_update_and_restart(new_exe_path):
    """创建并执行批处理脚本以替换旧文件并重启 (仅限Windows)。"""
    if os.name != 'nt':
        print("自动更新仅支持 Windows。请手动替换文件。")
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
    """下载指定的资产文件，并根据是否有父窗口显示不同进度条。"""
    download_url = asset_data.get("browser_download_url")
    filename = asset_data.get("name")

    try:
        print(f"准备下载: {filename}...")
        response = requests.get(download_url, stream=True, timeout=10)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))

        if parent_widget:  # GUI模式
            progress_dialog = QProgressDialog(f"正在下载 {filename}...", "取消", 0, total_size, parent_widget)
            progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
            progress_dialog.setValue(0)

            with open(filename, 'wb') as f:
                downloaded_size = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if progress_dialog.wasCanceled():
                        return None  # 下载被取消
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    progress_dialog.setValue(downloaded_size)
            return os.path.abspath(filename)

        else:  # CLI模式
            with open(filename, 'wb') as f, tqdm(
                    desc=f"下载中", total=total_size, unit='B',
                    unit_scale=True, unit_divisor=1024
            ) as bar:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    bar.update(len(chunk))
            return os.path.abspath(filename)

    except Exception as e:
        print(f"下载过程中发生错误: {e}")
        if parent_widget:
            QMessageBox.critical(parent_widget, "下载错误", f"下载更新时出错: {e}")
        return None


def check_for_updates(current_version, target_asset_keyword, parent_widget=None, silent=False):
    """
    检查 GitHub Release 以获取更新。

    Args:
        current_version (str): 当前应用程序的版本字符串 (例如, "2.4.0 GUI")。
        target_asset_keyword (str): 要在 Release 资产名称中查找的关键字 (例如, "falcon_gui" 或 "falcon_cli")。
        parent_widget (QWidget, optional): 用于显示消息框的父GUI窗口。如果为 None，则在控制台打印。
        silent (bool): 如果为 True，则只有在有更新时才显示消息，否则不显示任何内容。
    """
    if not silent:
        if parent_widget:
            QMessageBox.information(parent_widget, "检查更新", "正在连接到 GitHub 以检查新版本...")
        else:
            print("正在连接到 GitHub 以检查新版本...")

    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        latest_release = response.json()
        latest_tag = latest_release.get("tag_name", "0.0.0")
        latest_version_str = latest_tag.lstrip('v')

        current_version_tuple = _parse_version(current_version)
        latest_version_tuple = _parse_version(latest_version_str)

        if latest_version_tuple > current_version_tuple:
            # 发现新版本，准备提示信息
            # release_notes = latest_release.get("body", "没有提供更新说明。") # 不再获取更新内容
            message = (
                f"发现新版本！\n\n"
                f"当前版本: {current_version}\n"
                f"最新版本: {latest_version_str}\n\n"
                f"是否立即下载并更新？"
            )

            # 根据是否有父窗口决定如何提示
            if parent_widget:
                reply = QMessageBox.question(parent_widget, "发现新版本", message,
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    asset_to_download = next((asset for asset in latest_release.get("assets", [])
                                              if target_asset_keyword in asset.get("name", "").lower()), None)
                    if asset_to_download:
                        new_exe_path = download_asset(asset_to_download, parent_widget)
                        if new_exe_path:
                            _apply_update_and_restart(new_exe_path)
                    else:
                        QMessageBox.warning(parent_widget, "错误", f"在最新版本中未找到包含 '{target_asset_keyword}' 的文件。")
            else: # CLI 模式
                print("\n" + "="*60)
                print(f"发现新版本！ (当前: {current_version}, 最新: {latest_version_str})")
                # print(f"更新内容:\n{release_notes}") # 不再显示更新内容
                print("="*60 + "\n")
                choice = input("是否立即下载并更新？ (y/n): ").lower()
                if choice == 'y':
                    asset_to_download = next((asset for asset in latest_release.get("assets", [])
                                              if target_asset_keyword in asset.get("name", "").lower()), None)
                    if asset_to_download:
                        new_exe_path = download_asset(asset_to_download)
                        if new_exe_path:
                            _apply_update_and_restart(new_exe_path)
                    else:
                        print(f"错误: 在最新版本中未找到包含 '{target_asset_keyword}' 的文件。")
        else:
            # 只有在非静默模式下才提示“已是最新”
            if not silent:
                if parent_widget:
                    QMessageBox.information(parent_widget, "无需更新", f"您当前使用的版本 ({current_version}) 已是最新版本。")
                else:
                    print("您当前的版本已是最新。")

    except requests.exceptions.RequestException as e:
        # 只有在非静默模式下才提示网络错误
        if not silent:
            error_message = f"检查更新失败: 无法连接到服务器。\n请检查您的网络连接。\n\n错误: {e}"
            if parent_widget:
                QMessageBox.warning(parent_widget, "网络错误", error_message)
            else:
                print(error_message)
    except Exception as e:
        # 只有在非静默模式下才提示其他错误
        if not silent:
            error_message = f"检查更新时发生未知错误: {e}"
            if parent_widget:
                QMessageBox.critical(parent_widget, "更新错误", error_message)
            else:
                print(error_message)
