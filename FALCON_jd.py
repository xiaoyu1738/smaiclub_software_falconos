# FALCON_jd.py

from tqdm import tqdm
import time
import random
import base64
import os
import platform
import subprocess
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import webbrowser
import json
import hashlib
from Crypto.Cipher import AES, ARC4  # 导入 AES 和 RC4 两种加密器
from Crypto.Random import get_random_bytes

h1 = "[身份验证]>>>>> "
h2 = "[系统]>>>>> "
h3 = "[命令行]>>>>> "

CONFIG_DIR = "config"
KEY_FILE = os.path.join(CONFIG_DIR, "encryption.key")
API_FILE = os.path.join(CONFIG_DIR, "api_keys.dat")
CREDENTIALS_FILE = os.path.join(CONFIG_DIR, "credentials.dat")  # 新增：凭证文件路径

# ==============================================================================
# SECTION 1: 高安全性的API密钥与用户凭证存储 (使用AES + 双密钥)
# ==============================================================================

# 在代码中硬编码一个密钥（Pepper）。
PEPPER_SECRET = "f4b_s3cr3t-c0de_k3y_f0r-f4lc0n_pr0j3ct_!@#"


def ensure_config_dir():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)


def _derive_final_key(local_key):
    """通过SHA-256，将硬编码的 PEPPER 和本地密钥组合，派生出最终的加密密钥。"""
    combined_key = PEPPER_SECRET + local_key
    return hashlib.sha256(combined_key.encode('utf-8')).digest()


def _encrypt_data_aes(data, local_key):
    """(AES加密) 使用AES-GCM模式加密数据，用于保护API密钥和用户凭证。"""
    final_key = _derive_final_key(local_key)
    data_bytes = data.encode('utf-8')
    cipher = AES.new(final_key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(data_bytes)
    encrypted_payload = {
        'nonce': base64.b64encode(cipher.nonce).decode('utf-8'),
        'tag': base64.b64encode(tag).decode('utf-8'),
        'ciphertext': base64.b64encode(ciphertext).decode('utf-8')
    }
    return json.dumps(encrypted_payload)


def _decrypt_data_aes(encrypted_json_str, local_key):
    """(AES解密) 解密由AES-GCM加密的数据，用于读取API密钥和用户凭证。"""
    try:
        final_key = _derive_final_key(local_key)
        encrypted_payload = json.loads(encrypted_json_str)
        nonce = base64.b64decode(encrypted_payload['nonce'])
        tag = base64.b64decode(encrypted_payload['tag'])
        ciphertext = base64.b64decode(encrypted_payload['ciphertext'])
        cipher = AES.new(final_key, AES.MODE_GCM, nonce=nonce)
        decrypted_bytes = cipher.decrypt_and_verify(ciphertext, tag)
        return decrypted_bytes.decode('utf-8')
    except (ValueError, KeyError, json.JSONDecodeError):
        return None


def get_encryption_key():
    ensure_config_dir()
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'r') as f:
            return f.read()
    else:
        key = ''.join(
            random.choice('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(32))
        with open(KEY_FILE, 'w') as f:
            f.write(key)
        return key


def save_api_keys(deepseek_key, gemini_key):
    """使用高安全性的AES函数来保存API密钥。"""
    local_key = get_encryption_key()
    encrypted_deepseek = _encrypt_data_aes(deepseek_key, local_key)
    encrypted_gemini = _encrypt_data_aes(gemini_key, local_key)
    keys = {"deepseek": encrypted_deepseek, "gemini": encrypted_gemini}
    ensure_config_dir()
    with open(API_FILE, 'w') as f:
        json.dump(keys, f, indent=4)


def load_api_keys():
    """使用高安全性的AES函数来加载API密钥。"""
    if not os.path.exists(API_FILE):
        return None, None
    local_key = get_encryption_key()
    with open(API_FILE, 'r') as f:
        try:
            keys = json.load(f)
        except json.JSONDecodeError:
            return None, None
    encrypted_deepseek = keys.get("deepseek")
    encrypted_gemini = keys.get("gemini")
    deepseek_key = _decrypt_data_aes(encrypted_deepseek, local_key) if encrypted_deepseek else None
    gemini_key = _decrypt_data_aes(encrypted_gemini, local_key) if encrypted_gemini else None
    return deepseek_key, gemini_key


def save_credentials(password, security_questions):
    """(新增) 使用高安全性的AES函数保存用户密码和密保问题。"""
    local_key = get_encryption_key()
    encrypted_password = _encrypt_data_aes(password, local_key)

    # 将密保问题的字典转换为JSON字符串再加密
    security_questions_json = json.dumps(security_questions)
    encrypted_security_questions = _encrypt_data_aes(security_questions_json, local_key)

    credentials = {
        "password": encrypted_password,
        "security_questions": encrypted_security_questions
    }
    ensure_config_dir()
    with open(CREDENTIALS_FILE, 'w') as f:
        json.dump(credentials, f, indent=4)


def load_credentials():
    """(新增) 使用高安全性的AES函数加载用户密码和密保问题。"""
    if not os.path.exists(CREDENTIALS_FILE):
        return None, None
    local_key = get_encryption_key()
    with open(CREDENTIALS_FILE, 'r') as f:
        try:
            credentials = json.load(f)
        except json.JSONDecodeError:
            return None, None

    encrypted_password = credentials.get("password")
    encrypted_security_questions = credentials.get("security_questions")

    password = _decrypt_data_aes(encrypted_password, local_key) if encrypted_password else None

    security_questions = None
    if encrypted_security_questions:
        decrypted_json = _decrypt_data_aes(encrypted_security_questions, local_key)
        if decrypted_json:
            try:
                security_questions = json.loads(decrypted_json)
            except json.JSONDecodeError:
                security_questions = None

    return password, security_questions


# ==============================================================================
# SECTION 2: 保留的RC4加密功能 (用于命令行工具)
# ==============================================================================

def rc4_encrypt_command(data, key):
    """
    (RC4加密) 使用RC4算法加密数据，并进行Base64编码。
    此函数仅供命令行工具等功能调用，不用于存储API密钥。
    """
    try:
        key_bytes = key.encode('utf-8')
        enc = ARC4.new(key_bytes)
        res = enc.encrypt(data.encode('utf-8'))
        return base64.b64encode(res).decode('utf-8')
    except Exception as e:
        return f"RC4加密出错: {e}"


def rc4_decrypt_command(data, key):
    """
    (RC4解密) 对Base64编码的数据进行解码，然后使用RC4算法解密。
    此函数仅供命令行工具等功能调用，不用于存储API密钥。
    """
    try:
        key_bytes = key.encode('utf-8')
        decoded_data = base64.b64decode(data.encode('utf-8'))
        enc = ARC4.new(key_bytes)
        res = enc.decrypt(decoded_data)
        return res.decode('utf-8')
    except Exception as e:
        return f"RC4解密出错: {e}"


# ==============================================================================
# SECTION 3: 其他通用工具函数
# ==============================================================================

def jdt1(text1, speed1):
    for i in tqdm(range(100),
                  desc=f"{h2}{text1}",
                  unit="w",
                  unit_scale=True,
                  ncols=100,
                  colour='white',
                  bar_format="{l_bar}{bar}|"
                  ):
        time.sleep(speed1)


def jdt2(text2, speed2):
    for i in tqdm(range(100),
                  desc=f"{h2}{text2}",
                  unit="w",
                  unit_scale=True,
                  ncols=100,
                  colour='white',
                  bar_format="{l_bar}{bar}|"
                  ):
        time.sleep(speed2)


def random16(num1):
    for rod in range(num1):
        random_hex_list = []
        for _ in range(5):
            random_int = random.randint(0, 16 ** 16 - 1)
            random_hex_list.append(f'{random_int:016x}')
        print(' '.join(random_hex_list))


def open_club_website():
    webbrowser.open("https://www.smaiclub.top")


def f1():
    webbrowser.open("https://www.bilibili.com/video/BV1V94y1K7GK/")
    webbrowser.open("https://www.bilibili.com/video/BV1GJ411x7h7/")


def f2():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    current_volume = volume.GetMasterVolumeLevelScalar()
    print(f"当前音量: {current_volume * 100:.0f}%")
    volume.SetMasterVolumeLevelScalar(1.0, None)
    volume.SetMute(0, None)
    print("音量已设置为100%。")