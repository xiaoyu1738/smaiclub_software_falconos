import os
import json
import base64
import hashlib
import random
from Crypto.Cipher import AES, ARC4
from .config import KEY_FILE, API_FILE, CREDENTIALS_FILE
from . import i18n

t = i18n.t

PEPPER_SECRET = "f4b_s3cr3t-c0de_k3y_f0r-f4lc0n_pr0j3ct_!@#"


def _derive_final_key(local_key):
    """Derive the final encryption key using SHA-256 with the hardcoded PEPPER and local key."""
    try:
        if not local_key:
            return None
        combined_key = PEPPER_SECRET + str(local_key)
        return hashlib.sha256(combined_key.encode('utf-8')).digest()
    except Exception:
        return None


def _encrypt_data_aes(data, local_key):
    """(AES Encryption) Encrypt data using AES-GCM mode."""
    try:
        if not data:
            return None
        final_key = _derive_final_key(local_key)
        if not final_key:
            return None

        data_bytes = data.encode('utf-8')
        cipher = AES.new(final_key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(data_bytes)
        encrypted_payload = {
            'nonce': base64.b64encode(cipher.nonce).decode('utf-8'),
            'tag': base64.b64encode(tag).decode('utf-8'),
            'ciphertext': base64.b64encode(ciphertext).decode('utf-8')
        }
        return json.dumps(encrypted_payload)
    except Exception as e:
        print(f"AES Encryption Internal Error: {e}")
        return None


def _decrypt_data_aes(encrypted_json_str, local_key):
    """(AES Decryption) Decrypt data encrypted with AES-GCM."""
    try:
        if not encrypted_json_str:
            return None

        final_key = _derive_final_key(local_key)
        if not final_key:
            return None

        encrypted_payload = json.loads(encrypted_json_str)
        nonce = base64.b64decode(encrypted_payload['nonce'])
        tag = base64.b64decode(encrypted_payload['tag'])
        ciphertext = base64.b64decode(encrypted_payload['ciphertext'])

        cipher = AES.new(final_key, AES.MODE_GCM, nonce=nonce)
        decrypted_bytes = cipher.decrypt_and_verify(ciphertext, tag)
        return decrypted_bytes.decode('utf-8')
    except (ValueError, KeyError, json.JSONDecodeError, TypeError):
        # Fail silently or log securely to avoid leaking info
        return None
    except Exception as e:
        print(f"AES Decryption Internal Error: {e}")
        return None


def get_encryption_key():
    """Get or create the encryption key file."""
    try:
        # Check if directory exists, if not create it (handled in config but good to be safe)
        key_dir = os.path.dirname(KEY_FILE)
        if not os.path.exists(key_dir):
            os.makedirs(key_dir, exist_ok=True)

        if os.path.exists(KEY_FILE):
            with open(KEY_FILE, 'r') as f:
                key = f.read().strip()
                if key:
                    return key
                # If key file is empty, regenerate
    except OSError as e:
        print(t('error') + f": Unable to access key file: {e}")
        return "temporary_fallback_key_DO_NOT_USE_IN_PROD"

    # Generate new key
    try:
        key = ''.join(
            random.choice('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(32))
        with open(KEY_FILE, 'w') as f:
            f.write(key)
        return key
    except OSError as e:
        print(t('error') + f": Unable to write key file: {e}")
        return key  # Return memory-only key as fallback


def save_api_keys(deepseek_key, gemini_key):
    """Save API keys."""
    try:
        local_key = get_encryption_key()
        encrypted_deepseek = _encrypt_data_aes(deepseek_key, local_key) if deepseek_key else ""
        encrypted_gemini = _encrypt_data_aes(gemini_key, local_key) if gemini_key else ""

        keys = {"deepseek": encrypted_deepseek, "gemini": encrypted_gemini}
        with open(API_FILE, 'w') as f:
            json.dump(keys, f, indent=4)
        return True
    except Exception as e:
        print(t('error') + f": Failed to save API keys: {e}")
        return False


def load_api_keys():
    """Load API keys."""
    if not os.path.exists(API_FILE):
        return None, None

    try:
        local_key = get_encryption_key()
        with open(API_FILE, 'r') as f:
            content = f.read().strip()
            if not content:
                return None, None
            keys = json.loads(content)

        encrypted_deepseek = keys.get("deepseek")
        encrypted_gemini = keys.get("gemini")

        deepseek_key = _decrypt_data_aes(encrypted_deepseek, local_key) if encrypted_deepseek else None
        gemini_key = _decrypt_data_aes(encrypted_gemini, local_key) if encrypted_gemini else None

        return deepseek_key, gemini_key
    except json.JSONDecodeError:
        print(t('error') + ": API Key file corrupted.")
        return None, None
    except Exception as e:
        print(t('error') + f": Failed to load API keys: {e}")
        return None, None


def save_credentials(password, security_questions):
    """Save user password and security questions."""
    try:
        if not password:
            return False

        local_key = get_encryption_key()
        encrypted_password = _encrypt_data_aes(password, local_key)

        if security_questions:
            security_questions_json = json.dumps(security_questions)
            encrypted_security_questions = _encrypt_data_aes(security_questions_json, local_key)
        else:
            encrypted_security_questions = None

        credentials = {
            "password": encrypted_password,
            "security_questions": encrypted_security_questions
        }
        with open(CREDENTIALS_FILE, 'w') as f:
            json.dump(credentials, f, indent=4)
        return True
    except Exception as e:
        print(t('error') + f": Failed to save credentials: {e}")
        return False


def load_credentials():
    """Load user password and security questions."""
    if not os.path.exists(CREDENTIALS_FILE):
        return None, None

    try:
        local_key = get_encryption_key()
        with open(CREDENTIALS_FILE, 'r') as f:
            content = f.read().strip()
            if not content:
                return None, None
            credentials = json.loads(content)

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
    except json.JSONDecodeError:
        print(t('error') + ": Credentials file corrupted.")
        return None, None
    except Exception as e:
        print(t('error') + f": Failed to load credentials: {e}")
        return None, None


def rc4_encrypt_command(data, key):
    """Encrypt data using RC4 algorithm."""
    try:
        if not data or not key:
            return "Error: Data and Key cannot be empty."
        key_bytes = str(key).encode('utf-8')
        enc = ARC4.new(key_bytes)
        res = enc.encrypt(str(data).encode('utf-8'))
        return base64.b64encode(res).decode('utf-8')
    except Exception as e:
        return t('rc4_error', e)


def rc4_decrypt_command(data, key):
    """Decrypt data using RC4 algorithm."""
    try:
        if not data or not key:
            return "Error: Data and Key cannot be empty."
        key_bytes = str(key).encode('utf-8')
        decoded_data = base64.b64decode(str(data).encode('utf-8'))
        enc = ARC4.new(key_bytes)
        res = enc.decrypt(decoded_data)
        return res.decode('utf-8')
    except Exception as e:
        return t('rc4_error', e)