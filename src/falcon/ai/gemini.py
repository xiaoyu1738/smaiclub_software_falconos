# src/falcon/ai/gemini.py

import time
import google.generativeai as genai
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# AI Prefix for Gemini
AI_PREFIX = f"{Fore.GREEN}AI(Gemini)>>>>>> {Style.RESET_ALL}"
TYPEWRITER_SPEED = 0.03

def chat_gemini_stream(prompt, model_name, api_key):
    """
    Stream chat with Gemini API.
    """
    if not api_key:
        print(f"{AI_PREFIX}{Fore.RED}Error: Gemini API key not set. Please use 'setapikey' command.{Style.RESET_ALL}")
        return

    try:
        # Configure Gemini API
        genai.configure(api_key=api_key)

        # Create Generative Model instance
        model = genai.GenerativeModel(model_name)

        # Generate content with stream
        response = model.generate_content(prompt, stream=True)

        # Print AI Prefix
        print(AI_PREFIX, end="", flush=True)

        # Process stream response chunks
        for chunk in response:
            if chunk.text:
                for char in chunk.text:
                    print(f"{Fore.GREEN}{char}{Style.RESET_ALL}", end='', flush=True)
                    time.sleep(TYPEWRITER_SPEED)

        print()  # Newline after completion

    except Exception as e:
        print(f"\n{Fore.RED}Error communicating with Gemini API: {e}{Style.RESET_ALL}")
        print(
            f"{Fore.YELLOW}Please check your API key, network connection, or if model '{model_name}' is available.{Style.RESET_ALL}")
