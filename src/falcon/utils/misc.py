import random
import webbrowser
import platform

# Only import Windows-specific modules if on Windows
if platform.system() == "Windows":
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
    except ImportError:
        pass
else:
    # Dummy imports or implementations for non-Windows
    AudioUtilities = None
    IAudioEndpointVolume = None
    CLSCTX_ALL = None

def generate_random_passwords(count):
    """
    Generate a specified number of random passwords.
    Returns a list of passwords.
    """
    passwords = []
    # To maintain similar output volume to old behavior, generate count * 5
    total_passwords = count * 5
    if total_passwords == 0:
        return []

    for _ in range(total_passwords):
        random_int = random.randint(0, 16 ** 16 - 1)
        passwords.append(f'{random_int:016x}')
    return passwords

def open_club_website():
    webbrowser.open("https://www.smaiclub.top")

def open_easter_egg_videos():
    webbrowser.open("https://www.bilibili.com/video/BV1V94y1K7GK/")
    webbrowser.open("https://www.bilibili.com/video/BV1GJ411x7h7/")

def set_system_volume_max():
    """
    Sets the system volume to 100% and un-mutes.
    """
    if platform.system() != "Windows":
        print("Volume control is only supported on Windows.")
        return

    try:
        if AudioUtilities:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            current_volume = volume.GetMasterVolumeLevelScalar()
            print(f"Current Volume: {current_volume * 100:.0f}%")
            volume.SetMasterVolumeLevelScalar(1.0, None)
            volume.SetMute(0, None)
            print("Volume set to 100%.")
        else:
             print("Audio utilities not available.")
    except Exception as e:
        print(f"Failed to set volume: {e}")
