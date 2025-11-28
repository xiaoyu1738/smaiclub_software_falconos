# FALCON OS: Your Secure Command Line & GUI Companion

FALCON OS is a powerful, security-focused multi-platform application that offers two distinct experiences: an efficiency-built **Command Line Interface (CLI)** and a convenience-built **Graphical User Interface (GUI)**. Its core mission is to provide a smooth, secure AI chat experience, deeply integrated with industry-leading **DeepSeek** and **Google Gemini** large language models. We always prioritize your privacy, ensuring sensitive data like API keys and login credentials are securely stored on your local device using high-strength encryption.

## ✨ Core Highlights

* **Dual Interface Design**: Choose freely between the classic CLI and the modern PyQt6-based GUI.
* **Dual AI Engines**: Seamlessly integrate and switch between DeepSeek and Google Gemini models.
* **Financial-Grade Security**: Uses high-strength **AES-GCM encryption**, combining local random keys with internal "Pepper" for double protection.
* **Complete User Authentication**: Built-in login system. Default key is `114514`. Reset available via security questions.
* **Auto-Update**: Built-in update checker connects to GitHub for latest releases.
* **Powerful Toolkit**:
  * **File Encryption**: Securely encrypt/decrypt local files.
  * **Hash Calculator**: Calculate MD5, SHA-1, SHA-256.
  * **QR Code Generator**: Generate and save QR codes.
  * **Random Password Generator**: Create high-strength passwords.
  * **System Monitor**: View CPU and Memory usage.
  * **Proxy Settings**: Configure HTTP proxy for Gemini access.

## 🚀 Quick Start

### Option 1: Run from Source

1. **Prerequisites**: Python 3.8+.
2. **Clone**:
   ```bash
   git clone https://github.com/xiaoyu1738/smaiclub_software_falconos
   cd smaiclub_software_falconos
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run**:
   * CLI: `python run_cli.py`
   * GUI: `python run_gui.py`

### Option 2: Binary Releases
Download from [Releases Page](https://github.com/xiaoyu1738/smaiclub_software_falconos/releases).

## 📖 Usage Guide

1. **First Login**: Default key is `114514`.
2. **Initial Setup**:
   * Use `setpassword` (CLI) or Settings tab (GUI) to change your key and set security questions.
   * Use `setapikey` (CLI) or Settings tab (GUI) to save your DeepSeek/Gemini API keys.

## 🔒 Security Note
* Credentials and API keys are **never stored in plain text**.
* **AES-GCM** ensures confidentiality and integrity.

## 📄 License
GNU GPLv3. See `LICENSE`.

---
© 2025 SMAICLUB, FALCON STUDIO. All rights reserved.
