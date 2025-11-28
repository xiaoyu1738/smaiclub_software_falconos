# src/falcon/cli/main.py

import os
import time
import random
import sys
import psutil
import hashlib
import qrcode
from colorama import Fore, Style, init

# Local imports
from ..core import config, security, crypto, updater
from ..utils import ui, misc, logo
from ..ai import deepseek, gemini

# Initialize colorama
init(autoreset=True)

# Constants
CURRENT_VERSION = "2.5.0" # Updated version for this refactor
DOCUMENTS_PATH = "D:\\FALCON"  # Can be configurable

# Headers
h1 = "[Authentication]>>>>> "
h2 = "[System]>>>>> "
h3 = "[Command]>>>>> "
h4 = "[Time]>>>>> "
h5_deepseek = f"{Fore.BLUE}AI(DeepSeek)>>>>>> {Style.RESET_ALL}"

# Global State
current_proxy = "None"
deepseek_api_key = None
gemini_api_key = None
user_password = None
security_questions = None

def load_all_data():
    """Load all encrypted data."""
    global deepseek_api_key, gemini_api_key, user_password, security_questions
    deepseek_api_key, gemini_api_key = security.load_api_keys()
    user_password, security_questions = security.load_credentials()

def check_for_updates_automatic():
    """Check for updates on startup."""
    print(f"{h2}Checking for updates...")
    updater.check_for_updates(CURRENT_VERSION, "falcon_cli", parent_widget=None, silent=True)

def authentication_sequence():
    """Handles user login."""
    active_password = user_password if user_password else "114514"
    password_attempts = 3

    while password_attempts > 0:
        password_input = input(f"{h1}Enter Key: ")
        print(f"{h1}Verifying Key...")
        time.sleep(0.35)

        if password_input == active_password:
            print(f"{h1}Access Granted")
            return
        else:
            password_attempts -= 1
            if password_attempts > 0:
                print(f"{h1}{Fore.RED}Invalid Key. {password_attempts} attempts remaining.{Style.RESET_ALL}")
            else:
                print(f"{h1}{Fore.RED}Too many failed attempts.{Style.RESET_ALL}")

    print(f"{h2}Access Denied")
    logo.print_sb_logo()

    if user_password and security_questions:
        forgot_choice = input(f"{h1}Forgot Key? (y to reset, other to exit): ").lower()
        if forgot_choice == 'y':
            print(f"{h2}Starting Key Reset Procedure...")
            question = random.choice(list(security_questions.keys()))
            correct_answer = security_questions[question]
            user_answer = input(f"{h1}[Security Question]: {question}\n{h1}Answer: ")

            if user_answer == correct_answer:
                print(f"{h2}{Fore.GREEN}Verified! Set your new key.{Style.RESET_ALL}")
                while True:
                    new_password = input(f"{h1}Enter New Key: ")
                    confirm_password = input(f"{h1}Confirm New Key: ")
                    if new_password == confirm_password:
                        if new_password:
                            break
                        else:
                            print(f"{h1}{Fore.RED}Key cannot be empty.{Style.RESET_ALL}")
                    else:
                        print(f"{h1}{Fore.RED}Keys do not match.{Style.RESET_ALL}")

                security.save_credentials(new_password, security_questions)
                print(f"\n{h2}{Fore.GREEN}Key Reset Successful!{Style.RESET_ALL}")
                print(f"{h2}Please restart and login with the new key.")
            else:
                print(f"{h2}{Fore.RED}Incorrect Answer.{Style.RESET_ALL}")

    sys.exit(0)

def startup_animation():
    ui.show_progress_bar_type1("Connecting ", 0.01)
    print("")
    ui.show_progress_bar_type1("Sending Request ", 0.001)
    print("")
    for i in range(1, 33):
        ui.show_progress_bar_type1(f"Starting Core H{i} ", 0.001)
        print("")
    for i in range(1, 33):
        ui.show_progress_bar_type1(f"Checking Core H{i} Status ", 0.0001)
        print("")

    time.sleep(0.5)
    print(f"{h2}Cores Active")
    time.sleep(0.2)
    print(f"{h2}Connection Stable")
    time.sleep(0.2)
    ui.show_progress_bar_type1("Starting Security Protocols ", 0.001)
    print("")
    time.sleep(0.2)
    ui.show_progress_bar_type1("Starting Main Program ", 0.01)
    print("")
    time.sleep(0.5)
    print("")
    print(f"{h2}Startup Complete")
    print("")
    logo.print_smaiclub_logo()
    print(f"{h2}System Online...")
    print("================================================================================")
    print(f"{h3}Command Line Online. Type 'help' for commands.")

def main_loop():
    global user_password, security_questions, deepseek_api_key, gemini_api_key, current_proxy

    while True:
        cmd = input(f"{h3}").strip()

        if cmd == "help":
            print(f"{h3}Available Commands")
            print(
                '''
help ------ Show available commands
exit ------ Exit program
time ------ Show system time
sysinfo --- Show device info
diag ------ Run system diagnostics
randompa -- Generate random passwords
surprise -- A surprise
ai -------- Open AI chat
proxy ----- Set/View HTTP Proxy
RC4 ------- RC4 Encryption/Decryption
crypto ---- AES File Encryption/Decryption
smaiclub -- Open SMAICLUB website
setapikey - Set AI API Keys
setpassword Set software key and security questions
update ---- Check for updates
hash ------ Calculate file/text hash
monitor --- System resource monitor
qrcode ---- Generate QR Code
info ------ Show version info
                '''
            )

        elif cmd == "exit":
            print("Exiting...")
            time.sleep(0.5)
            print("System Shutdown")
            sys.exit(0)

        elif cmd == "info":
            print(f"FALCON OS v{CURRENT_VERSION}")
            print("Copyright (c) 2025 SMAICLUB Software")
            print("https://github.com/xiaoyu1738/smaiclub_software_falconos")

        elif cmd == "update":
            updater.check_for_updates(CURRENT_VERSION, "falcon_cli", parent_widget=None)

        elif cmd == "time":
             print(h4, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

        elif cmd == "sysinfo":
            print("[Device Info]")
            print("Core: Quantum Neural Net v2.86")
            print("Processor: Photonic Array v5.69")
            print("Memory: 42PB @ 9877654232MHz")
            print("Storage: 1.685672YB Quantum Crystal")
            print("Network: Global Quantum Backbone")
            print("Security Level: 114514")

        elif cmd == "diag":
            ui.show_progress_bar_type2("Checking Core Status ", 0.5)
            ui.show_progress_bar_type2("Checking System Status ", 0.1)
            print("Core Status: Normal")
            print("System Status: Normal")

        elif cmd == "smaiclub":
            misc.open_club_website()
            print(f"{h2}Website Opened.")

        elif cmd == "surprise":
            print("DO NOT WEAR HEADPHONES")
            time.sleep(1)
            print("3")
            time.sleep(1)
            print("2")
            time.sleep(1)
            print("1")
            time.sleep(1)
            misc.set_system_volume_max()
            misc.open_easter_egg_videos()

        elif cmd == "randompa":
            try:
                num_input = input(f"{h3}Number of passwords (default 5): ")
                num_to_generate = int(num_input) if num_input.isdigit() and int(num_input) > 0 else 5
            except ValueError:
                num_to_generate = 5

            print(f"{h2}Generating {num_to_generate} passwords...")
            passwords = misc.generate_random_passwords(num_to_generate)
            # generate_random_passwords returns count*5, so slice it
            passwords = passwords[:num_to_generate]

            print(f"{h2}Passwords:")
            for i in range(0, len(passwords), 4):
                print("  " + " ".join(passwords[i:i + 4]))

            save_choice = input(f"\n{h3}Save to file? (y/n): ").lower()
            if save_choice == 'y':
                timestamp = time.strftime('%Y%m%d_%H%M%S')
                filename = f"passwords_{timestamp}.txt"
                save_path = os.path.join(DOCUMENTS_PATH, filename)
                try:
                    with open(save_path, 'w', encoding='utf-8') as f:
                         f.write(f"--- FALCON OS Passwords ---\n")
                         for p in passwords:
                             f.write(p + '\n')
                    print(f"{h2}{Fore.GREEN}Saved to: {os.path.abspath(save_path)}{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{h2}{Fore.RED}Error saving: {e}{Style.RESET_ALL}")

        elif cmd == "monitor":
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                print("\n--- Monitor ---")
                print(f"{Fore.CYAN}CPU: {cpu_percent}%{Style.RESET_ALL}")
                print(f"{Fore.GREEN}RAM: {memory.used / (1024**3):.2f} GB / {memory.total / (1024**3):.2f} GB{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Disk: {disk.used / (1024**3):.2f} GB / {disk.total / (1024**3):.2f} GB{Style.RESET_ALL}")
                print("----------------\n")
            except Exception as e:
                 print(f"{h2}{Fore.RED}Monitor Error: {e}{Style.RESET_ALL}")

        elif cmd == "hash":
            print("1. Text Hash")
            print("2. File Hash")
            choice = input(f"{h3}Choice: ")
            if choice == '1':
                text = input(f"{h3}Text: ").encode('utf-8')
                print(f"MD5: {hashlib.md5(text).hexdigest()}")
                print(f"SHA1: {hashlib.sha1(text).hexdigest()}")
                print(f"SHA256: {hashlib.sha256(text).hexdigest()}")
            elif choice == '2':
                path = input(f"{h3}File Path: ")
                if os.path.exists(path):
                     with open(path, 'rb') as f:
                        data = f.read()
                        print(f"MD5: {hashlib.md5(data).hexdigest()}")
                        print(f"SHA1: {hashlib.sha1(data).hexdigest()}")
                        print(f"SHA256: {hashlib.sha256(data).hexdigest()}")
                else:
                    print("File not found.")

        elif cmd == "qrcode":
            data = input(f"{h3}Text/URL: ")
            if not data: continue
            print("1. Show in Terminal")
            print("2. Save as PNG")
            c = input(f"{h3}Choice: ")
            if c == '1':
                qr = qrcode.QRCode()
                qr.add_data(data)
                qr.make(fit=True)
                qr.print_tty()
            elif c == '2':
                fname = input(f"{h3}Filename (e.g. code.png): ")
                if not fname.endswith('.png'): fname += '.png'
                path = os.path.join(DOCUMENTS_PATH, fname)
                qrcode.make(data).save(path)
                print(f"Saved to {path}")

        elif cmd == "RC4":
            print("1. Encrypt  2. Decrypt")
            c = input(f"{h3}Choice: ")
            if c == '1':
                d = input("Text: ")
                k = input("Key: ")
                print(f"Result: {security.rc4_encrypt_command(d, k)}")
            elif c == '2':
                d = input("Text: ")
                k = input("Key: ")
                print(f"Result: {security.rc4_decrypt_command(d, k)}")

        elif cmd == "crypto":
             print("1. Encrypt File  2. Decrypt File")
             c = input(f"{h3}Choice: ")
             path = input("File Path: ")
             pwd = input("Password: ")
             if c == '1':
                 crypto.encrypt_file_aes(path, pwd)
             elif c == '2':
                 crypto.decrypt_file_aes(path, pwd)

        elif cmd == "setpassword":
             print(f"{h2}Set New Key")
             # Verify old
             old = input(f"{h1}Current Key: ")
             if old != (user_password if user_password else "114514"):
                 print("Invalid Key.")
                 continue

             new_p = input("New Key: ")
             if not new_p: continue

             print("Set 3 Security Questions:")
             qs = {}
             for i in range(3):
                 q = input(f"Question {i+1}: ")
                 a = input("Answer: ")
                 qs[q] = a

             security.save_credentials(new_p, qs)
             user_password = new_p
             security_questions = qs
             print("Saved.")

        elif cmd == "setapikey":
            print(f"{h2}Set API Keys (Press Enter to keep current)")
            ds = input("DeepSeek Key: ").strip()
            gm = input("Gemini Key: ").strip()

            final_ds = ds if ds else deepseek_api_key
            final_gm = gm if gm else gemini_api_key

            security.save_api_keys(final_ds, final_gm)
            deepseek_api_key = final_ds
            gemini_api_key = final_gm
            print("Saved.")

        elif cmd.startswith("proxy"):
             parts = cmd.split()
             if len(parts) == 1:
                 print(f"Current Proxy: {current_proxy}")
             elif parts[1] == "clear":
                 os.environ.pop('HTTP_PROXY', None)
                 os.environ.pop('HTTPS_PROXY', None)
                 current_proxy = "None"
                 print("Proxy Cleared.")
             elif parts[1] == "help":
                 print("Use: proxy http://127.0.0.1:7890")
             else:
                 p = parts[1]
                 os.environ['HTTP_PROXY'] = p
                 os.environ['HTTPS_PROXY'] = p
                 current_proxy = p
                 print(f"Proxy set to {p}")

        elif cmd == "ai":
             if not deepseek_api_key and not gemini_api_key:
                 print("No API Keys set.")
                 continue
             print("1. DeepSeek")
             print("2. Gemini")
             c = input("Choice: ")
             if c == '1':
                 if not deepseek_api_key:
                     print("DeepSeek Key missing.")
                     continue
                 print("DeepSeek Chat (type 'aiquit' to exit)")
                 while True:
                     p = input(h5_deepseek)
                     if p == 'aiquit': break
                     deepseek.chat_deepseek_stream(p, deepseek_api_key)
             elif c == '2':
                 if not gemini_api_key:
                     print("Gemini Key missing.")
                     continue
                 print("Gemini Chat (type 'aiquit' to exit)")
                 while True:
                     p = input(f"{Fore.GREEN}AI(Gemini)>>>>>> {Style.RESET_ALL}")
                     if p == 'aiquit': break
                     gemini.chat_gemini_stream(p, "gemini-pro", gemini_api_key) # Defaulting to pro for simplicity

        else:
            print(f"Unknown command: {cmd}")

def run():
    # Ensure doc path
    global DOCUMENTS_PATH
    if not os.path.exists(DOCUMENTS_PATH):
        try:
            os.makedirs(DOCUMENTS_PATH)
        except OSError:
            DOCUMENTS_PATH = "."

    load_all_data()
    logo.print_big_logo_falcon()
    authentication_sequence()
    check_for_updates_automatic()
    startup_animation()
    main_loop()

if __name__ == "__main__":
    run()
