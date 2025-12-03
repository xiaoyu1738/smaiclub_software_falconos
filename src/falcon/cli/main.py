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
from ..core import config, security, crypto, updater, i18n
from ..utils import ui, misc, logo
from ..ai import deepseek, gemini

# Initialize colorama
init(autoreset=True)

# Constants
CURRENT_VERSION = "2.5.03"
DOCUMENTS_PATH = os.path.join(os.path.expanduser('~'), 'Documents', 'FALCON')
if not os.path.exists(DOCUMENTS_PATH):
    os.makedirs(DOCUMENTS_PATH, exist_ok=True)

# Helper for translation
t = i18n.t

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
    print(f"{t('sys_header')}{t('checking_updates')}")
    updater.check_for_updates(CURRENT_VERSION, "falcon_cli", parent_widget=None, silent=True)

def authentication_sequence():
    """Handles user login."""
    active_password = user_password if user_password else "114514"
    password_attempts = 3

    while password_attempts > 0:
        password_input = input(f"{t('auth_header')}{t('enter_key')}")
        print(f"{t('auth_header')}{t('verifying_key')}")
        time.sleep(0.35)

        if password_input == active_password:
            print(f"{t('auth_header')}{t('access_granted')}")
            return
        else:
            password_attempts -= 1
            if password_attempts > 0:
                print(f"{t('auth_header')}{Fore.RED}{t('invalid_key', password_attempts)}{Style.RESET_ALL}")
            else:
                print(f"{t('auth_header')}{Fore.RED}{t('too_many_attempts')}{Style.RESET_ALL}")

    print(f"{t('sys_header')}{t('access_denied')}")
    logo.print_sb_logo()

    if user_password and security_questions:
        forgot_choice = input(f"{t('auth_header')}{t('forgot_key_prompt')}").lower()
        if forgot_choice == 'y':
            print(f"{t('sys_header')}{t('starting_reset')}")
            question = random.choice(list(security_questions.keys()))
            correct_answer = security_questions[question]
            user_answer = input(f"{t('auth_header')}{t('security_question', question)}")

            if user_answer == correct_answer:
                print(f"{t('sys_header')}{Fore.GREEN}{t('verified_set_new')}{Style.RESET_ALL}")
                while True:
                    new_password = input(f"{t('auth_header')}{t('enter_new_key')}")
                    confirm_password = input(f"{t('auth_header')}{t('confirm_new_key')}")
                    if new_password == confirm_password:
                        if new_password:
                            break
                        else:
                            print(f"{t('auth_header')}{Fore.RED}{t('key_empty')}{Style.RESET_ALL}")
                    else:
                        print(f"{t('auth_header')}{Fore.RED}{t('keys_mismatch')}{Style.RESET_ALL}")

                security.save_credentials(new_password, security_questions)
                print(f"\n{t('sys_header')}{Fore.GREEN}{t('reset_success')}{Style.RESET_ALL}")
                print(f"{t('sys_header')}{t('restart_login')}")
            else:
                print(f"{t('sys_header')}{Fore.RED}{t('incorrect_answer')}{Style.RESET_ALL}")

    sys.exit(0)

def startup_animation():
    ui.show_progress_bar_type1(t('cli_connecting'), 0.01)
    print("")
    ui.show_progress_bar_type1(t('cli_sending_req'), 0.001)
    print("")
    for i in range(1, 15): # Reduced count for brevity
        ui.show_progress_bar_type1(t('cli_starting_core', i), 0.001)
        print("")

    time.sleep(0.5)
    print(f"{t('sys_header')}{t('core_status')}")
    time.sleep(0.2)
    print(f"{t('sys_header')}{t('sys_status')}")
    time.sleep(0.2)
    ui.show_progress_bar_type1(t('cli_security_proto'), 0.001)
    print("")
    time.sleep(0.2)
    ui.show_progress_bar_type1(t('cli_starting_main'), 0.01)
    print("")
    time.sleep(0.5)
    print("")
    print(f"{t('sys_header')}{t('startup_complete')}")
    print("")
    logo.print_smaiclub_logo()
    print(f"{t('sys_header')}{t('system_online')}")
    print("================================================================================")
    print(f"{t('cmd_header')}{t('cli_online')}")

def main_loop():
    global user_password, security_questions, deepseek_api_key, gemini_api_key, current_proxy

    while True:
        cmd = input(f"{t('cmd_header')}").strip()

        if cmd == "help":
            print(f"{t('cmd_header')}{t('available_commands')}")
            print(t('cmd_help'))
            print(t('cmd_exit'))
            print(t('cmd_time'))
            print(t('cmd_sysinfo'))
            print(t('cmd_diag'))
            print(t('cmd_randompa'))
            print(t('cmd_surprise'))
            print(t('cmd_ai'))
            print(t('cmd_proxy'))
            print(t('cmd_rc4'))
            print(t('cmd_crypto'))
            print(t('cmd_smaiclub'))
            print(t('cmd_setapikey'))
            print(t('cmd_setpassword'))
            print(t('cmd_update'))
            print(t('cmd_hash'))
            print(t('cmd_monitor'))
            print(t('cmd_qrcode'))
            print(t('cmd_info'))
            print(t('cmd_setlang'))

        elif cmd == "exit":
            print(t('exiting'))
            time.sleep(0.5)
            print(t('shutdown'))
            sys.exit(0)

        elif cmd == "info":
            print(f"FALCON OS v{CURRENT_VERSION}")
            print("Copyright (c) 2025 SMAICLUB Software")
            print("https://github.com/xiaoyu1738/smaiclub_software_falconos")

        elif cmd == "update":
            updater.check_for_updates(CURRENT_VERSION, "falcon_cli", parent_widget=None)

        elif cmd == "time":
             print(t('time_header'), time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

        elif cmd == "sysinfo":
            print(t('device_info'))
            print("Core: Quantum Neural Net v2.86")
            print("Processor: Photonic Array v5.69")
            print("Memory: 42PB @ 9877654232MHz")
            print("Storage: 1.685672YB Quantum Crystal")
            print("Network: Global Quantum Backbone")
            print("Security Level: 114514")

        elif cmd == "diag":
            ui.show_progress_bar_type2("Checking Core Status ", 0.5)
            ui.show_progress_bar_type2("Checking System Status ", 0.1)
            print(t('core_status'))
            print(t('sys_status'))

        elif cmd == "smaiclub":
            misc.open_club_website()
            print(f"{t('sys_header')}{t('website_opened')}")

        elif cmd == "surprise":
            print(t('surprise_warning'))
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
                num_input = input(f"{t('cmd_header')}{t('gen_pass_prompt')}")
                num_to_generate = int(num_input) if num_input.isdigit() and int(num_input) > 0 else 5
            except ValueError:
                num_to_generate = 5

            print(f"{t('sys_header')}{t('generating_pass', num_to_generate)}")
            passwords = misc.generate_random_passwords(num_to_generate)
            passwords = passwords[:num_to_generate]

            print(f"{t('sys_header')}{t('passwords_header')}")
            for i in range(0, len(passwords), 4):
                print("  " + " ".join(passwords[i:i + 4]))

            save_choice = input(f"\n{t('cmd_header')}{t('save_prompt')}").lower()
            if save_choice == 'y':
                timestamp = time.strftime('%Y%m%d_%H%M%S')
                filename = f"passwords_{timestamp}.txt"
                save_path = os.path.join(DOCUMENTS_PATH, filename)
                try:
                    with open(save_path, 'w', encoding='utf-8') as f:
                         f.write(f"--- FALCON OS Passwords ---\n")
                         for p in passwords:
                             f.write(p + '\n')
                    print(f"{t('sys_header')}{Fore.GREEN}{t('saved_to', os.path.abspath(save_path))}{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{t('sys_header')}{Fore.RED}{t('error_saving', e)}{Style.RESET_ALL}")

        elif cmd == "monitor":
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                print(f"\n{t('monitor_header')}")
                print(f"{Fore.CYAN}{t('monitor_cpu', cpu_percent)}{Style.RESET_ALL}")
                print(f"{Fore.GREEN}{t('monitor_ram', memory.used / (1024**3), memory.total / (1024**3))}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}{t('monitor_disk', disk.used / (1024**3), disk.total / (1024**3))}{Style.RESET_ALL}")
                print("----------------\n")
            except Exception as e:
                 print(f"{t('sys_header')}{Fore.RED}Monitor Error: {e}{Style.RESET_ALL}")

        elif cmd == "hash":
            print(t('hash_menu'))
            choice = input(f"{t('cmd_header')}{t('choice')}")
            if choice == '1':
                text = input(f"{t('cmd_header')}{t('text_input')}").encode('utf-8')
                print(f"MD5: {hashlib.md5(text).hexdigest()}")
                print(f"SHA1: {hashlib.sha1(text).hexdigest()}")
                print(f"SHA256: {hashlib.sha256(text).hexdigest()}")
            elif choice == '2':
                path = input(f"{t('cmd_header')}{t('file_path')}")
                if os.path.exists(path):
                     with open(path, 'rb') as f:
                        data = f.read()
                        print(f"MD5: {hashlib.md5(data).hexdigest()}")
                        print(f"SHA1: {hashlib.sha1(data).hexdigest()}")
                        print(f"SHA256: {hashlib.sha256(data).hexdigest()}")
                else:
                    print(t('file_not_found'))

        elif cmd == "qrcode":
            data = input(f"{t('cmd_header')}{t('qr_input')}")
            if not data: continue
            print(t('qr_menu'))
            c = input(f"{t('cmd_header')}{t('choice')}")
            if c == '1':
                qr = qrcode.QRCode()
                qr.add_data(data)
                qr.make(fit=True)
                qr.print_tty()
            elif c == '2':
                fname = input(f"{t('cmd_header')}{t('filename')}")
                if not fname.endswith('.png'): fname += '.png'
                path = os.path.join(DOCUMENTS_PATH, fname)
                qrcode.make(data).save(path)
                print(f"Saved to {path}")

        elif cmd == "RC4":
            print(t('rc4_menu'))
            c = input(f"{t('cmd_header')}{t('choice')}")
            if c == '1':
                d = input(t('text_input'))
                k = input(t('key_input'))
                print(t('result', security.rc4_encrypt_command(d, k)))
            elif c == '2':
                d = input(t('text_input'))
                k = input(t('key_input'))
                print(t('result', security.rc4_decrypt_command(d, k)))

        elif cmd == "crypto":
             print(t('crypto_menu'))
             c = input(f"{t('cmd_header')}{t('choice')}")
             path = input(t('file_path'))
             pwd = input(t('password_input'))
             if c == '1':
                 crypto.encrypt_file_aes(path, pwd)
             elif c == '2':
                 crypto.decrypt_file_aes(path, pwd)

        elif cmd == "setpassword":
             print(f"{t('sys_header')}{t('set_new_key_header')}")
             old = input(f"{t('auth_header')}{t('current_key')}")
             if old != (user_password if user_password else "114514"):
                 print(t('invalid_key', 0))
                 continue

             new_p = input(t('enter_new_key'))
             if not new_p: continue

             print(t('set_sq_header'))
             qs = {}
             for i in range(3):
                 q = input(t('question_n', i+1))
                 a = input(t('answer_input'))
                 qs[q] = a

             security.save_credentials(new_p, qs)
             user_password = new_p
             security_questions = qs
             print(t('saved'))

        elif cmd == "setapikey":
            print(f"{t('sys_header')}{t('set_api_header')}")
            ds = input(t('ds_key')).strip()
            gm = input(t('gm_key')).strip()

            final_ds = ds if ds else deepseek_api_key
            final_gm = gm if gm else gemini_api_key

            security.save_api_keys(final_ds, final_gm)
            deepseek_api_key = final_ds
            gemini_api_key = final_gm
            print(t('saved'))

        elif cmd.startswith("proxy"):
             parts = cmd.split()
             if len(parts) == 1:
                 print(t('proxy_current', current_proxy))
             elif parts[1] == "clear":
                 os.environ.pop('HTTP_PROXY', None)
                 os.environ.pop('HTTPS_PROXY', None)
                 current_proxy = "None"
                 print(t('proxy_cleared'))
             elif parts[1] == "help":
                 print(t('proxy_help'))
             else:
                 p = parts[1]
                 os.environ['HTTP_PROXY'] = p
                 os.environ['HTTPS_PROXY'] = p
                 current_proxy = p
                 print(t('proxy_set', p))

        elif cmd == "ai":
             if not deepseek_api_key and not gemini_api_key:
                 print(t('ai_no_keys'))
                 continue
             print(t('ai_menu'))
             c = input(t('choice'))
             if c == '1':
                 if not deepseek_api_key:
                     print(t('ai_ds_missing'))
                     continue
                 print(t('ai_ds_start'))
                 while True:
                     p = input(f"{Fore.BLUE}AI(DeepSeek)>>>>>> {Style.RESET_ALL}")
                     if p == 'aiquit': break
                     deepseek.chat_deepseek_stream(p, deepseek_api_key)
             elif c == '2':
                 if not gemini_api_key:
                     print(t('ai_gm_missing'))
                     continue
                 print(t('ai_gm_start'))
                 while True:
                     p = input(f"{Fore.GREEN}AI(Gemini)>>>>>> {Style.RESET_ALL}")
                     if p == 'aiquit': break
                     gemini.chat_gemini_stream(p, "gemini-pro", gemini_api_key)

        elif cmd == "setlang":
            print(t('select_lang'))
            print("1. English")
            print("2. 简体中文")
            print("3. 繁體中文")
            print("4. Español")
            print("5. Français")
            print("6. Deutsch")
            print("7. 日本語")
            print("8. Русский")

            lang_map = {
                "1": "en", "2": "zh-CN", "3": "zh-TW", "4": "es",
                "5": "fr", "6": "de", "7": "ja", "8": "ru"
            }
            c = input(t('choice'))
            if c in lang_map:
                i18n.save_language(lang_map[c])
                print(t('lang_set', i18n.LANGUAGES[lang_map[c]]))
            else:
                print("Invalid choice.")

        else:
            print(t('unknown_cmd', cmd))

def run():
    load_all_data()
    logo.print_big_logo_falcon()
    authentication_sequence()
    check_for_updates_automatic()
    startup_animation()
    main_loop()

if __name__ == "__main__":
    run()