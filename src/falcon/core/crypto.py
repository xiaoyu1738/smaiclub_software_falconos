import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from . import i18n

t = i18n.t


def generate_key_from_password(password: str, salt: bytes) -> bytes:
    """Generates a key from a password and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key


def encrypt_file_aes(file_path: str, password: str):
    """Encrypts a file and deletes the original."""
    try:
        # Check for empty path
        if not file_path:
            print(t('crypto_file_not_found', "Empty Path"))
            return False

        if not os.path.exists(file_path):
            print(t('crypto_file_not_found', file_path))
            return False

        # Security Check: Ensure path is a file, not a directory
        if not os.path.isfile(file_path):
            print(t('encryption_error', f"Path is not a file: {file_path}"))
            return False

        confirm = input(t('crypto_encrypt_warning', os.path.basename(file_path))).lower()
        if confirm != 'y':
            print(t('operation_canceled'))
            return False

        salt = os.urandom(16)
        key = generate_key_from_password(password, salt)
        fernet = Fernet(key)

        with open(file_path, 'rb') as file:
            original = file.read()

        encrypted = fernet.encrypt(original)

        encrypted_file_path = file_path + '.enc'
        with open(encrypted_file_path, 'wb') as encrypted_file:
            encrypted_file.write(salt + encrypted)

        os.remove(file_path)

        print(t('file_encrypted_to', encrypted_file_path))
        print(t('source_deleted', os.path.basename(file_path)))
        return True
    except FileNotFoundError:
        print(t('crypto_file_not_found', file_path))
        return False
    except OSError as e:
        # Catches invalid paths, permission errors, etc.
        print(t('encryption_error', f"System Error: {e}"))
        return False
    except Exception as e:
        print(t('encryption_error', e))
        return False


def decrypt_file_aes(file_path: str, password: str):
    """Decrypts a file and deletes the encrypted source."""
    try:
        # Check for empty path
        if not file_path:
            print(t('crypto_file_not_found', "Empty Path"))
            return False

        if not os.path.exists(file_path):
            print(t('crypto_file_not_found', file_path))
            return False

        # Security Check: Ensure path is a file, not a directory
        if not os.path.isfile(file_path):
            print(t('decryption_error', f"Path is not a file: {file_path}"))
            return False

        confirm = input(t('crypto_decrypt_warning', os.path.basename(file_path))).lower()
        if confirm != 'y':
            print(t('operation_canceled'))
            return False

        with open(file_path, 'rb') as encrypted_file:
            data = encrypted_file.read()

        salt = data[:16]
        encrypted_data = data[16:]

        key = generate_key_from_password(password, salt)
        fernet = Fernet(key)

        decrypted = fernet.decrypt(encrypted_data)

        original_file_path = file_path.replace('.enc', '')
        with open(original_file_path, 'wb') as decrypted_file:
            decrypted_file.write(decrypted)

        os.remove(file_path)

        print(t('file_decrypted_to', original_file_path))
        print(t('encrypted_deleted', os.path.basename(file_path)))
        return True
    except FileNotFoundError:
        print(t('crypto_file_not_found', file_path))
        return False
    except OSError as e:
        # Catches invalid paths, permission errors, etc.
        print(t('decryption_error', f"System Error: {e}"))
        return False
    except Exception as e:
        print(t('decryption_error', e))
        return False