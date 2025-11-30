import PyInstaller.__main__
import os
import platform
import sys


def build():
    # 1. 环境检测与配置
    # ---------------------------------------------------------
    # 获取当前操作系统名称
    os_name = platform.system()

    # PyInstaller --add-data 参数的分隔符：Windows 使用 ';', Linux/macOS 使用 ':'
    path_sep = ';' if os_name == 'Windows' else ':'

    # 资源文件配置: 将项目根目录下的 resources 文件夹打包进 exe 内部的 resources 目录
    # 格式: "源路径{分隔符}目标路径"
    add_data_arg = f'resources{path_sep}resources'

    # 图标文件路径
    icon_path = os.path.join('resources', 'favicon.ico')

    # 2. 定义隐藏导入 (Hidden Imports)
    # ---------------------------------------------------------
    # 这些库可能无法被 PyInstaller 自动检测到，需要手动指定
    common_hidden_imports = [
        '--hidden-import=google.generativeai',
        '--hidden-import=PIL',
        '--hidden-import=qrcode',
    ]

    # Windows 特有的依赖库
    if os_name == 'Windows':
        common_hidden_imports.extend([
            '--hidden-import=pycaw',
            '--hidden-import=comtypes',
        ])

    # 3. 构建 CLI (命令行版)
    # ---------------------------------------------------------
    print(f"[{os_name}] 正在构建 FALCON OS CLI...")

    cli_args = [
                   'run_cli.py',  # 脚本入口
                   '--onefile',  # 打包成单文件
                   '--name=FALCON_CLI',  # 输出文件名
                   '--clean',  # 构建前清理缓存
                   f'--add-data={add_data_arg}',  # 添加资源文件
               ] + common_hidden_imports

    # 执行构建
    PyInstaller.__main__.run(cli_args)
    print(">>> FALCON_CLI 构建完成。\n")

    # 4. 构建 GUI (图形界面版)
    # ---------------------------------------------------------
    print(f"[{os_name}] 正在构建 FALCON OS GUI...")

    gui_args = [
                   'run_gui.py',  # 脚本入口
                   '--onefile',  # 打包成单文件
                   '--windowed',  # 运行时不显示控制台窗口 (Windows/Mac有效)
                   '--name=FALCON_GUI',  # 输出文件名
                   '--clean',  # 构建前清理缓存
                   f'--icon={icon_path}',  # 设置应用程序图标
                   f'--add-data={add_data_arg}',  # 添加资源文件
               ] + common_hidden_imports

    # 执行构建
    PyInstaller.__main__.run(gui_args)
    print(">>> FALCON_GUI 构建完成。")


if __name__ == "__main__":
    # 检查是否在项目根目录运行
    if os.path.exists('run_cli.py') and os.path.exists('resources'):
        try:
            build()
            print("\n" + "=" * 50)
            print("所有构建任务已完成！请查看 'dist' 目录。")
            print("=" * 50)
        except Exception as e:
            print(f"\n构建失败: {e}")
    else:
        print("错误: 请将此脚本放在项目根目录 (包含 run_cli.py 和 resources 文件夹的位置) 运行。")