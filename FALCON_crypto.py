import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def generate_key(password: str, salt: bytes) -> bytes:
    """Generates a key from a password and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

def encrypt_file(file_path: str, password: str):
    """Encrypts a file and deletes the original."""
    try:
        if not os.path.exists(file_path):
            print(f"错误: 文件 '{file_path}' 未找到。")
            return False

        confirm = input(f"警告: 加密操作将删除源文件 '{os.path.basename(file_path)}'。是否继续? (y/n): ").lower()
        if confirm != 'y':
            print("操作已取消。")
            return False

        salt = os.urandom(16)
        key = generate_key(password, salt)
        fernet = Fernet(key)

        with open(file_path, 'rb') as file:
            original = file.read()

        encrypted = fernet.encrypt(original)

        encrypted_file_path = file_path + '.enc'
        with open(encrypted_file_path, 'wb') as encrypted_file:
            encrypted_file.write(salt + encrypted)

        os.remove(file_path)

        print(f"文件已加密并保存为: {encrypted_file_path}")
        print(f"源文件 '{os.path.basename(file_path)}' 已被删除。")
        return True
    except FileNotFoundError:
        print(f"错误: 文件 '{file_path}' 未找到。")
        return False
    except Exception as e:
        print(f"加密过程中发生错误: {e}")
        return False


def decrypt_file(file_path: str, password: str):
    """Decrypts a file and deletes the encrypted source."""
    try:
        if not os.path.exists(file_path):
            print(f"错误: 文件 '{file_path}' 未找到。")
            return False

        confirm = input(f"警告: 解密操作将删除加密文件 '{os.path.basename(file_path)}'。是否继续? (y/n): ").lower()
        if confirm != 'y':
            print("操作已取消。")
            return False

        with open(file_path, 'rb') as encrypted_file:
            data = encrypted_file.read()

        salt = data[:16]
        encrypted_data = data[16:]

        key = generate_key(password, salt)
        fernet = Fernet(key)

        decrypted = fernet.decrypt(encrypted_data)

        original_file_path = file_path.replace('.enc', '')
        with open(original_file_path, 'wb') as decrypted_file:
            decrypted_file.write(decrypted)

        os.remove(file_path)

        print(f"文件已解密并保存为: {original_file_path}")
        print(f"加密文件 '{os.path.basename(file_path)}' 已被删除。")
        return True
    except FileNotFoundError:
        print(f"错误: 文件 '{file_path}' 未找到。")
        return False
    except Exception as e:
        print(f"解密过程中发生错误: {e}")
        return False
