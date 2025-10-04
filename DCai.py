# DCai.py

import time
from openai import OpenAI
from colorama import init, Fore, Style

# 初始化colorama，使颜色设置在所有终端中生效
init(autoreset=True)

# --- 常量定义 ---
# AI模型名称
MODEL_NAME = "deepseek-chat"
# DeepSeek API的基础URL
BASE_URL = "https://api.deepseek.com"
# AI聊天前缀（蓝色以区分）
AI_PREFIX = f"{Fore.BLUE}AI(DeepSeek)>>>>>> {Style.RESET_ALL}"
# 打字机效果的速度（秒/字符）
TYPEWRITER_SPEED = 0.03


def ai1(prompt: str, api_key: str):
    """
    使用DeepSeek API进行流式聊天。

    该函数会检查API密钥是否存在，然后向DeepSeek API发送请求，
    并以打字机效果逐字流式输出响应。

    参数:
        prompt (str): 用户输入的内容。
        api_key (str): 用于认证的DeepSeek API密钥。
    """
    # 1. 检查API密钥
    if not api_key:
        print(f"{AI_PREFIX}{Fore.RED}错误: DeepSeek API密钥未设置。请使用 'setapikey' 命令进行设置。{Style.RESET_ALL}")
        return

    # 2. 初始化客户端
    try:
        client = OpenAI(api_key=api_key, base_url=BASE_URL)
    except Exception as e:
        print(f"\n{Fore.RED}初始化OpenAI客户端时发生错误: {e}{Style.RESET_ALL}")
        return

    # 3. 发送请求并处理响应
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": prompt},
            ],
            stream=True
        )

        # 打印AI前缀
        print(AI_PREFIX, end="", flush=True)

        # 以打字机效果流式输出内容
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                for char in content:
                    print(f"{Fore.BLUE}{char}{Style.RESET_ALL}", end='', flush=True)
                    time.sleep(TYPEWRITER_SPEED)

        print()  # 结束后换行

    except Exception as e:
        print(f"\n{Fore.RED}与DeepSeek API交互时发生错误: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}请检查您的API密钥是否正确、网络连接是否正常。{Style.RESET_ALL}")
