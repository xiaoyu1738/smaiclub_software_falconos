import os
import platform

def get_config_dir():
    """
    Get the user-specific configuration directory path to avoid permission issues.
    - Windows: C:/Users/Username/AppData/Roaming/FALCON
    - macOS:   /Users/Username/Library/Application Support/FALCON
    - Linux:   /home/Username/.config/FALCON
    """
    system = platform.system()

    if system == 'Windows':
        base_path = os.getenv('APPDATA')
    elif system == 'Darwin':  # macOS
        base_path = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support')
    else:  # Linux and other Unix-like systems
        base_path = os.path.join(os.path.expanduser('~'), '.config')

    # Fallback to current directory if base_path is not found
    if not base_path:
        base_path = '.'

    config_path = os.path.join(base_path, "FALCON")

    # Ensure the directory exists
    os.makedirs(config_path, exist_ok=True)

    return config_path

# Define all configuration file paths
CONFIG_DIR = get_config_dir()
KEY_FILE = os.path.join(CONFIG_DIR, "encryption.key")
API_FILE = os.path.join(CONFIG_DIR, "api_keys.dat")
CREDENTIALS_FILE = os.path.join(CONFIG_DIR, "credentials.dat")
