import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

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
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' not found.")
            return False

        confirm = input(f"Warning: Encryption will delete source file '{os.path.basename(file_path)}'. Continue? (y/n): ").lower()
        if confirm != 'y':
            print("Operation canceled.")
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

        print(f"File encrypted to: {encrypted_file_path}")
        print(f"Source file '{os.path.basename(file_path)}' deleted.")
        return True
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return False
    except Exception as e:
        print(f"Encryption error: {e}")
        return False


def decrypt_file_aes(file_path: str, password: str):
    """Decrypts a file and deletes the encrypted source."""
    try:
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' not found.")
            return False

        confirm = input(f"Warning: Decryption will delete encrypted file '{os.path.basename(file_path)}'. Continue? (y/n): ").lower()
        if confirm != 'y':
            print("Operation canceled.")
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

        print(f"File decrypted to: {original_file_path}")
        print(f"Encrypted file '{os.path.basename(file_path)}' deleted.")
        return True
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return False
    except Exception as e:
        print(f"Decryption error: {e}")
        return False
