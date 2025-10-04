# DCai_Gemini.py

import time
import google.generativeai as genai
from colorama import init, Fore, Style

# 初始化colorama
init(autoreset=True)

# 设置Gemini的AI聊天前缀（绿色以区分）
h5 = f"{Fore.GREEN}AI(Gemini)>>>>>> {Style.RESET_ALL}"

def ai_gemini_chat(prompt, model_name, api_key):
    """
    使用指定的Gemini模型与API进行流式聊天。

    参数:
    prompt (str): 用户输入的内容。
    model_name (str): 要使用的Gemini模型名称 (例如 'gemini-pro')。
    api_key (str): 用于认证的Gemini API密钥。
    """
    if not api_key:
        print(f"{h5}{Fore.RED}错误: Gemini API密钥未设置。请使用 'setapikey' 命令进行设置。{Style.RESET_ALL}")
        return

    try:
        # 配置Gemini API
        genai.configure(api_key=api_key)

        # 创建一个生成模型实例
        model = genai.GenerativeModel(model_name)

        # 以流式方式生成内容
        response = model.generate_content(prompt, stream=True)

        # 打印AI前缀
        print(h5, end="", flush=True)

        # 逐块处理流式响应，实现打字机效果
        for chunk in response:
            # 检查chunk中是否有文本内容
            if chunk.text:
                for char in chunk.text:
                    print(f"{Fore.GREEN}{char}{Style.RESET_ALL}", end='', flush=True)
                    time.sleep(0.03)  # 控制打字速度

        print()  # 结束后换行

    except Exception as e:
        print(f"\n{Fore.RED}与Gemini API交互时发生错误: {e}{Style.RESET_ALL}")
        print(
            f"{Fore.YELLOW}请检查你的API密钥是否正确、网络连接是否正常，或所选模型 '{model_name}' 是否可用。{Style.RESET_ALL}")