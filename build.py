import sys
import os
import platform
import subprocess
import shutil


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
    运行 PyInstaller 并直接显示其 INFO 级别的日志
    """
    # 构造命令
    # 移除 --log-level=ERROR，使用默认的 INFO 级别，这样会输出白色文字的详细过程
    cmd = [sys.executable, '-m', 'PyInstaller', script_name] + extra_args

    print(f"\n>>> 开始构建 {target_name} ...")
    print("-" * 60)

    try:
        # 直接调用 subprocess.run，不捕获 stdout/stderr，让其直接输出到终端
        # 这样就能看到 PyInstaller 原生的白色日志滚动效果
        result = subprocess.run(cmd, text=True)

        print("-" * 60)
        if result.returncode == 0:
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