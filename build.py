import sys
import os
import platform
import subprocess
import shutil
import time

# 尝试导入 tqdm，如果不存在则提示
try:
    from tqdm import tqdm
except ImportError:
    print("错误: 未找到 'tqdm' 模块。请运行: pip install tqdm")
    sys.exit(1)


def clean_previous_builds():
    """清理之前的构建残留"""
    dirs_to_clean = ['build', 'dist']
    print("[1/3] 清理旧的构建文件...")
    for d in dirs_to_clean:
        if os.path.exists(d):
            try:
                shutil.rmtree(d)
            except Exception as e:
                print(f"  - 警告: 无法清理 {d}: {e}")


def run_pyinstaller(target_name, script_name, extra_args):
    """
    运行 PyInstaller 并显示进度条，隐藏详细日志
    """
    # 构造命令
    cmd = [sys.executable, '-m', 'PyInstaller', script_name] + extra_args + ['--log-level=ERROR']

    # 进度条描述
    desc = f"正在构建 {target_name}"

    try:
        # 启动子进程，捕获输出
        # bufsize=1 表示行缓冲，确保我们能实时读取输出
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # 将 stderr 合并到 stdout
            text=True,
            encoding='utf-8',
            errors='replace',  # 防止编码错误导致崩溃
            bufsize=1
        )

        # 使用 tqdm 显示进度
        # 由于无法预知 PyInstaller 会输出多少行日志，这里主要展示"正在处理"的状态
        with tqdm(desc=desc, unit="op", leave=True, dynamic_ncols=True) as pbar:
            for _ in process.stdout:
                # 每读取到一行日志（即完成一步操作），进度条+1
                pbar.update(1)

        process.wait()

        if process.returncode == 0:
            print(f"✅ {target_name} 构建成功！")
            return True
        else:
            print(f"❌ {target_name} 构建失败。")
            return False

    except KeyboardInterrupt:
        print("\n构建已取消。")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return False


def main():
    # 1. 环境准备
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)  # 确保在脚本所在目录运行

    clean_previous_builds()

    # 2. 平台配置
    os_name = platform.system()
    path_sep = ';' if os_name == 'Windows' else ':'

    # 资源文件: "源路径{分隔符}目标路径"
    # 注意：resources 文件夹必须存在
    if not os.path.exists("resources"):
        print("错误: 当前目录下未找到 resources 文件夹！")
        sys.exit(1)

    add_data_arg = f'resources{path_sep}resources'
    icon_path = os.path.join('resources', 'favicon.ico')

    # 通用隐藏导入
    hidden_imports = [
        '--hidden-import=google.generativeai',
        '--hidden-import=PIL',
        '--hidden-import=qrcode',
    ]

    # Windows 特有导入
    if os_name == 'Windows':
        hidden_imports.extend([
            '--hidden-import=pycaw',
            '--hidden-import=comtypes',
        ])

    print("[2/3] 开始构建 CLI 版本...")
    # CLI 构建参数
    cli_args = [
                   '--onefile',
                   '--name=FALCON_CLI',
                   '--clean',
                   f'--add-data={add_data_arg}',
               ] + hidden_imports

    run_pyinstaller("FALCON_CLI", "run_cli.py", cli_args)

    print("\n[3/3] 开始构建 GUI 版本...")
    # GUI 构建参数
    gui_args = [
                   '--onefile',
                   '--windowed',  # 隐藏控制台
                   '--name=FALCON_GUI',
                   '--clean',
                   f'--icon={icon_path}',
                   f'--add-data={add_data_arg}',
               ] + hidden_imports

    run_pyinstaller("FALCON_GUI", "run_gui.py", gui_args)

    print("\n" + "=" * 50)
    print(f"🎉 所有任务完成！可执行文件位于: {os.path.join(base_dir, 'dist')}")
    print("=" * 50)


if __name__ == "__main__":
    main()