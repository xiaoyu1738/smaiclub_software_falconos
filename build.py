import sys
import os
import platform
import subprocess
import shutil
import time

# 优先尝试导入 rich (更美观)，如果不存在则回退到 tqdm
use_rich = False
try:
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.console import Console

    use_rich = True
except ImportError:
    try:
        from tqdm import tqdm
    except ImportError:
        print("错误: 未找到 'rich' 或 'tqdm' 模块。建议运行: pip install rich")
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
    运行 PyInstaller 并显示可视化进度条
    """
    # 构造命令
    # 移除 --log-level=WARN，我们需要 PyInstaller 的标准输出流来驱动进度条动画
    cmd = [sys.executable, '-m', 'PyInstaller', script_name] + extra_args

    try:
        # 启动子进程，捕获输出
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # 将 stderr 合并到 stdout
            text=True,
            encoding='utf-8',
            errors='replace',  # 防止编码错误导致崩溃
            bufsize=1
        )

        if use_rich:
            # === 使用 Rich 显示现代化进度条 ===
            console = Console()
            with Progress(
                    SpinnerColumn("dots", style="bold cyan"),  # 动态转圈图标
                    TextColumn("[bold blue]{task.description}"),
                    # 移除 style="black" 以避免在黑色终端背景下看不到进度条槽
                    BarColumn(bar_width=None, pulse_style="bright_green"),
                    # 添加状态文本列，显示当前正在处理的日志片段（截断显示）
                    TextColumn("[dim cyan]{task.fields[status]}"),
                    TimeElapsedColumn(),  # 耗时显示
                    console=console,
                    transient=False  # 完成后保留显示
            ) as progress:
                # total=None 启用不确定(脉冲)模式，status 初始化
                task = progress.add_task(f"正在构建 {target_name}...", total=None, status="初始化...")

                for line in process.stdout:
                    # 获取日志行并清理，作为状态显示
                    current_status = line.strip()
                    if current_status:
                        # 截取过长的日志，避免破坏布局 (保留前30个字符)
                        display_status = (current_status[:30] + '...') if len(current_status) > 30 else current_status
                        progress.update(task, advance=1, status=display_status)
                    else:
                        progress.update(task, advance=1)

        else:
            # === Fallback: 使用 tqdm (但也美化一下) ===
            desc = f"正在构建 {target_name}"
            # 绿色进度条，更紧凑的格式
            with tqdm(desc=desc, unit="op", leave=True, dynamic_ncols=True,
                      bar_format="{l_bar}{bar}| [{elapsed}]", colour='green') as pbar:
                for _ in process.stdout:
                    pbar.update(1)

        process.wait()

        if process.returncode == 0:
            if use_rich:
                # 构建完成后，清除状态文字，显示简单的成功信息
                console.print(f"✅ [bold green]{target_name} 构建成功！[/]")
            else:
                print(f"✅ {target_name} 构建成功！")
            return True
        else:
            if use_rich:
                console.print(f"❌ [bold red]{target_name} 构建失败。[/]")
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

    # 资源文件检查
    if not os.path.exists("resources"):
        print("错误: 当前目录下未找到 resources 文件夹！")
        sys.exit(1)

    add_data_arg = f'resources{path_sep}resources'
    icon_path = os.path.join('resources', 'favicon.ico')

    # 定义依赖和路径
    # ---------------------------------------------------------------------
    # 关键修复: 添加 '--paths=src'，告诉 PyInstaller 在 src 目录下查找模块
    # ---------------------------------------------------------------------
    common_args = [
        '--onefile',
        '--clean',
        f'--add-data={add_data_arg}',
        '--paths=src',  # <--- 这里是修复 ModuleNotFoundError 的关键
        '--hidden-import=google.generativeai',
        '--hidden-import=PIL',
        '--hidden-import=qrcode',
    ]

    # Windows 特有导入
    if os_name == 'Windows':
        common_args.extend([
            '--hidden-import=pycaw',
            '--hidden-import=comtypes',
        ])

    print("[2/3] 开始构建 CLI 版本...")
    # CLI 构建参数
    cli_args = common_args + ['--name=FALCON_CLI']
    run_pyinstaller("FALCON_CLI", "run_cli.py", cli_args)

    print("\n[3/3] 开始构建 GUI 版本...")
    # GUI 构建参数
    gui_args = common_args + [
        '--name=FALCON_GUI',
        '--windowed',  # 隐藏控制台
        f'--icon={icon_path}'
    ]
    run_pyinstaller("FALCON_GUI", "run_gui.py", gui_args)

    print("\n" + "=" * 50)
    print(f"🎉 所有任务完成！可执行文件位于: {os.path.join(base_dir, 'dist')}")
    print("=" * 50)


if __name__ == "__main__":
    main()