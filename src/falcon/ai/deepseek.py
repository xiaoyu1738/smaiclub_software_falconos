# src/falcon/ai/deepseek.py

import time
from openai import OpenAI
from colorama import init, Fore, Style
from ..core import i18n

t = i18n.t

# Initialize colorama
init(autoreset=True)

# --- Constants ---
MODEL_NAME = "deepseek-chat"
BASE_URL = "https://api.deepseek.com"
AI_PREFIX = f"{Fore.BLUE}AI(DeepSeek)>>>>>> {Style.RESET_ALL}"
TYPEWRITER_SPEED = 0.03

def chat_deepseek_stream(prompt: str, api_key: str):
    """
    Stream chat with DeepSeek API.
    """
    # 1. Check API Key
    if not api_key:
        print(f"{AI_PREFIX}{Fore.RED}{t('ai_ds_error_key')}{Style.RESET_ALL}")
        return

    # 2. Initialize Client
    try:
        client = OpenAI(api_key=api_key, base_url=BASE_URL)
    except Exception as e:
        print(f"\n{Fore.RED}{t('ai_init_error', e)}{Style.RESET_ALL}")
        return

    # 3. Send Request and Handle Response
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": prompt},
            ],
            stream=True
        )

        # Print AI Prefix
        print(AI_PREFIX, end="", flush=True)

        # Stream output with typewriter effect
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                for char in content:
                    print(f"{Fore.BLUE}{char}{Style.RESET_ALL}", end='', flush=True)
                    time.sleep(TYPEWRITER_SPEED)

        print()  # Newline after completion

    except Exception as e:
        print(f"\n{Fore.RED}{t('ai_comm_error', e)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{t('ai_check_key')}{Style.RESET_ALL}")