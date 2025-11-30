# src/falcon/gui/main.py

import sys
import os
import time
import random
import hashlib
import qrcode
from PIL import Image

from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLineEdit, QLabel, QMessageBox, QDialog, QTabWidget, QTextEdit,
                             QComboBox, QFileDialog, QSpinBox, QGridLayout, QInputDialog,
                             QSplashScreen, QDialogButtonBox)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QIcon, QPixmap, QImage, QFont, QTextCursor, QPainter

# Local imports
from ..core import config, security, crypto, updater, i18n
from ..utils import ui, misc
from ..ai import deepseek, gemini

from openai import OpenAI, AuthenticationError
import google.generativeai as genai

# Helper for translation
t = i18n.t

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    # Check if the path exists directly (PyInstaller) or if it's in resources folder (Dev)
    full_path = os.path.join(base_path, relative_path)
    if not os.path.exists(full_path):
        # Try finding it in resources/ folder
        full_path = os.path.join(base_path, "resources", relative_path)

    return full_path

# --- Global Variables and Constants ---
CURRENT_VERSION = "2.5.0 GUI"
DOCUMENTS_PATH = os.path.join(os.path.expanduser('~'), 'Documents', 'FALCON')
if not os.path.exists(DOCUMENTS_PATH):
    os.makedirs(DOCUMENTS_PATH, exist_ok=True)

deepseek_api_key = None
gemini_api_key = None
user_password = None
security_questions = None

# --- QSS Stylesheet (Modern Dark Theme) ---
STYLESHEET = """
    QWidget {
        background-color: #2b2b2b;
        color: #f0f0f0;
        font-family: "Segoe UI", "Microsoft YaHei";
    }
    QTabWidget::pane {
        border-top: 2px solid #3c3c3c;
    }
    QTabBar::tab {
        background: #2b2b2b;
        border: 1px solid #3c3c3c;
        padding: 10px;
        min-width: 100px;
    }
    QTabBar::tab:selected {
        background: #3c3f41;
        border-bottom-color: #3c3f41;
    }
    QTabBar::tab:!selected:hover {
        background: #3c3c3c;
    }
    QLineEdit, QTextEdit, QComboBox, QSpinBox {
        background-color: #3c3c3c;
        border: 1px solid #555;
        border-radius: 4px;
        padding: 5px;
    }
    QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
        border: 1px solid #007acc;
    }
    QPushButton {
        background-color: #007acc;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #008ae6;
    }
    QPushButton:pressed {
        background-color: #006bb3;
    }
    QLabel {
        background-color: transparent;
    }
    QMessageBox {
        background-color: #3c3c3c;
    }
    QMessageBox QPushButton {
        min-width: 80px;
    }
"""

# --- Background Worker Threads ---

class AIWorker(QThread):
    new_token = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, prompt, model_info, api_key):
        super().__init__()
        self.prompt = prompt
        self.model_info = model_info
        self.api_key = api_key

    def run(self):
        try:
            if self.model_info['type'] == 'deepseek':
                client = OpenAI(api_key=self.api_key, base_url=deepseek.BASE_URL)
                response = client.chat.completions.create(
                    model=deepseek.MODEL_NAME, messages=[{"role": "user", "content": self.prompt}], stream=True
                )
                for chunk in response:
                    content = chunk.choices[0].delta.content
                    if content: self.new_token.emit(content)

            elif self.model_info['type'] == 'gemini':
                genai.configure(api_key=self.api_key)
                model = genai.GenerativeModel(self.model_info['name'])
                response = model.generate_content(self.prompt, stream=True)
                for chunk in response:
                    if chunk.text: self.new_token.emit(chunk.text)

        except (AuthenticationError, genai.types.PermissionDeniedError):
            self.error.emit("API Request Failed: Invalid API Key. Please check settings.")
        except Exception as e:
            error_message = str(e)
            if "API key" in error_message:
                self.error.emit("API Request Failed: Invalid API Key.")
            else:
                self.error.emit(f"API Request Failed: {e}")
        finally:
            self.finished.emit()


class CryptoWorker(QThread):
    finished = pyqtSignal(bool, str)

    def __init__(self, file_path, password, mode):
        super().__init__()
        self.file_path = file_path
        self.password = password
        self.mode = mode

    def run(self):
        original_input = __builtins__.input
        __builtins__.input = lambda _: 'y' # Mock input for auto-confirmation
        try:
            if self.mode == 'encrypt':
                result = crypto.encrypt_file_aes(self.file_path, self.password)
                if result: self.finished.emit(True, f"File encrypted to {self.file_path}.enc")
                else: self.finished.emit(False, "Encryption failed. Check console.")
            elif self.mode == 'decrypt':
                result = crypto.decrypt_file_aes(self.file_path, self.password)
                if result: self.finished.emit(True, f"File decrypted to {self.file_path.replace('.enc', '')}")
                else: self.finished.emit(False, "Decryption failed. Check console.")
        except Exception as e:
            self.finished.emit(False, f"Error: {e}")
        finally:
            __builtins__.input = original_input

# --- GUI Windows ---

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t('gui_about_title'))
        self.setMinimumSize(550, 450)

        self.info_text = f"""
<b>Copyright © 2025 SMAICLUB Software</b><br>
All rights reserved.<br><br>
<b>FALCON_OS Application</b><br>
Version: {CURRENT_VERSION}<br><br>
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.<br><br>
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.<br><br>
You should have received a copy of the GNU General Public License along with this program. If not, see <a href="http://www.gnu.org/licenses/">http://www.gnu.org/licenses/</a>.<br><br>
<b>Repository:</b> <a href="https://www.github.com/xiaoyu1738/smaiclub_software_falconos">https://www.github.com/xiaoyu1738/smaiclub_software_falconos</a>
"""
        # --- Layout ---
        layout = QVBoxLayout(self)

        # Logo
        logo_label = QLabel()
        pixmap = QPixmap(resource_path("logo.png"))
        logo_label.setPixmap(pixmap.scaledToWidth(200, Qt.TransformationMode.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)

        # Info Text
        self.info_label = QLabel(self.info_text)
        self.info_label.setWordWrap(True)
        self.info_label.setOpenExternalLinks(True)
        layout.addWidget(self.info_label)

        # Close Button
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)


class SplashScreen(QSplashScreen):
    def __init__(self):
        original_pixmap = QPixmap(resource_path("logo.png"))
        if original_pixmap.isNull():
             # Fallback if logo not found
             original_pixmap = QPixmap(300, 300)
             original_pixmap.fill(Qt.GlobalColor.black)

        text_margin = 50
        new_width = original_pixmap.width()
        new_height = original_pixmap.height() + text_margin
        composite_pixmap = QPixmap(new_width, new_height)
        composite_pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(composite_pixmap)
        painter.drawPixmap(0, 0, original_pixmap)
        painter.end()
        super().__init__(composite_pixmap)

        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.showMessage(t('gui_init'),
                         Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter,
                         Qt.GlobalColor.white)
    def update_message(self, msg):
        self.showMessage(msg,
                         Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter,
                         Qt.GlobalColor.white)

    def show_message(self, msg):
        self.showMessage(msg, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter, Qt.GlobalColor.white)

class SetPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t('gui_set_key_title'))
        self.setMinimumWidth(450)
        self.layout = QGridLayout(self)

        self.current_pass = QLineEdit(echoMode=QLineEdit.EchoMode.Password)
        self.new_pass = QLineEdit(echoMode=QLineEdit.EchoMode.Password)
        self.confirm_pass = QLineEdit(echoMode=QLineEdit.EchoMode.Password)

        self.q1 = QLineEdit(placeholderText=t('gui_q1'))
        self.a1 = QLineEdit(placeholderText=t('gui_a1'))
        self.q2 = QLineEdit(placeholderText=t('gui_q2'))
        self.a2 = QLineEdit(placeholderText=t('gui_a2'))
        self.q3 = QLineEdit(placeholderText=t('gui_q3'))
        self.a3 = QLineEdit(placeholderText=t('gui_a3'))

        self.save_button = QPushButton(t('gui_save_settings'))

        self.layout.addWidget(QLabel(t('current_key')), 0, 0)
        self.layout.addWidget(self.current_pass, 0, 1)
        self.layout.addWidget(QLabel(t('enter_new_key')), 1, 0)
        self.layout.addWidget(self.new_pass, 1, 1)
        self.layout.addWidget(QLabel(t('gui_confirm_new')), 2, 0)
        self.layout.addWidget(self.confirm_pass, 2, 1)

        self.layout.addWidget(QLabel(t('gui_sq_header')), 3, 0, 1, 2)
        self.layout.addWidget(self.q1, 4, 0)
        self.layout.addWidget(self.a1, 4, 1)
        self.layout.addWidget(self.q2, 5, 0)
        self.layout.addWidget(self.a2, 5, 1)
        self.layout.addWidget(self.q3, 6, 0)
        self.layout.addWidget(self.a3, 6, 1)
        self.layout.addWidget(self.save_button, 7, 0, 1, 2)

        self.save_button.clicked.connect(self.save_credentials)

    def save_credentials(self):
        global user_password, security_questions

        current_pass_to_check = user_password if user_password else "114514"
        if self.current_pass.text() != current_pass_to_check:
            QMessageBox.warning(self, "Validation Failed", t('invalid_key', 0))
            return

        if not self.new_pass.text() or self.new_pass.text() != self.confirm_pass.text():
            QMessageBox.warning(self, "Error", t('keys_mismatch'))
            return

        questions = {
            self.q1.text().strip(): self.a1.text().strip(),
            self.q2.text().strip(): self.a2.text().strip(),
            self.q3.text().strip(): self.a3.text().strip(),
        }
        if any(not q or not a for q, a in questions.items()):
            QMessageBox.warning(self, "Error", "All questions and answers must be filled.")
            return

        security.save_credentials(self.new_pass.text(), questions)
        user_password = self.new_pass.text()
        security_questions = questions

        QMessageBox.information(self, "Success", t('saved'))
        self.accept()

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(t('gui_login_title'))
        self.setWindowIcon(QIcon(resource_path("favicon.ico")))
        self.setFixedSize(350, 150)
        self.attempts_left = 3
        self.active_password = user_password if user_password else "114514"
        layout = QVBoxLayout(self)
        self.password_input = QLineEdit(echoMode=QLineEdit.EchoMode.Password, placeholderText=t('enter_key'))
        login_button = QPushButton(t('gui_login_btn'))
        forgot_button = QPushButton(t('gui_forgot_btn'))
        layout.addWidget(QLabel(t('enter_key')))
        layout.addWidget(self.password_input)
        button_layout = QHBoxLayout()
        button_layout.addWidget(forgot_button)
        button_layout.addWidget(login_button)
        layout.addLayout(button_layout)
        login_button.clicked.connect(self.check_password)
        forgot_button.clicked.connect(self.forgot_password)
        self.password_input.returnPressed.connect(self.check_password)

    def check_password(self):
        if self.password_input.text() == self.active_password:
            self.accept()
        else:
            self.attempts_left -= 1
            if self.attempts_left > 0:
                QMessageBox.warning(self, "Error", t('invalid_key', self.attempts_left))
            else:
                QMessageBox.critical(self, "Access Denied", t('too_many_attempts'))
                self.reject()

    def forgot_password(self):
        if not user_password or not security_questions:
            QMessageBox.warning(self, "Cannot Reset", "No user key or security questions set.")
            return

        question = random.choice(list(security_questions.keys()))
        answer, ok = QInputDialog.getText(self, "Security Question", t('security_question', question))

        if ok and answer and answer.strip() == security_questions[question]:
            new_password, ok = QInputDialog.getText(self, "Reset Key", t('verified_set_new'), QLineEdit.EchoMode.Password)
            if ok and new_password:
                confirm_password, ok = QInputDialog.getText(self, "Confirm Key", t('confirm_new_key'), QLineEdit.EchoMode.Password)
                if ok and new_password == confirm_password:
                    security.save_credentials(new_password, security_questions)
                    QMessageBox.information(self, "Success", t('reset_success'))
                    self.reject()
                else:
                    QMessageBox.warning(self, "Error", t('keys_mismatch'))
        else:
            QMessageBox.critical(self, "Failed", t('incorrect_answer'))

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(t('gui_title', CURRENT_VERSION))
        self.setWindowIcon(QIcon(resource_path("favicon.ico")))
        self.setGeometry(100, 100, 950, 750)
        self.ai_worker = None
        self.crypto_worker = None
        self.qr_pixmap = None
        self._init_ui()

        # Silent update check
        QTimer.singleShot(1500, self.check_for_updates_auto_silent)

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        self._create_tabs()
        main_layout.addWidget(self.tabs)
        self.status_bar = QLabel(t('gui_ready'))
        main_layout.addWidget(self.status_bar)
        self._connect_signals()

    def _create_tabs(self):
        self.tabs = QTabWidget()
        self._create_ai_tab()
        self._create_crypto_tab()
        self._create_tools_tab()
        self._create_settings_tab()

    def _create_ai_tab(self):
        tab_ai = QWidget()
        layout = QVBoxLayout(tab_ai)
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel(t('gui_ai_select')))
        self.ai_model_combo = QComboBox()
        self.ai_models = {
            "DeepSeek": {"type": "deepseek", "name": "deepseek-chat"},
            "Gemini Pro": {"type": "gemini", "name": "gemini-2.5-pro"},
            "Gemini Flash": {"type": "gemini", "name": "gemini-flash-latest"},
        }
        self.ai_model_combo.addItems(self.ai_models.keys())
        model_layout.addWidget(self.ai_model_combo)
        layout.addLayout(model_layout)
        self.ai_history = QTextEdit(readOnly=True)
        layout.addWidget(self.ai_history)
        input_layout = QHBoxLayout()
        self.ai_input = QLineEdit(placeholderText=t('gui_ai_input'))
        self.ai_send_button = QPushButton(t('gui_ai_send'))
        input_layout.addWidget(self.ai_input)
        input_layout.addWidget(self.ai_send_button)
        layout.addLayout(input_layout)
        self.tabs.addTab(tab_ai, t('gui_tab_ai'))

    def _create_crypto_tab(self):
        tab_crypto = QWidget()
        layout = QGridLayout(tab_crypto)
        self.crypto_file_path = QLineEdit(placeholderText=t('gui_file_path'), readOnly=True)
        browse_button = QPushButton(t('gui_browse'))
        self.crypto_password = QLineEdit(echoMode=QLineEdit.EchoMode.Password, placeholderText=t('password_input'))
        encrypt_button = QPushButton(t('gui_encrypt_btn'))
        decrypt_button = QPushButton(t('gui_decrypt_btn'))
        layout.addWidget(QLabel(t('gui_file_path')), 0, 0)
        layout.addWidget(self.crypto_file_path, 0, 1)
        layout.addWidget(browse_button, 0, 2)
        layout.addWidget(QLabel(t('password_input')), 1, 0)
        layout.addWidget(self.crypto_password, 1, 1, 1, 2)
        layout.addWidget(encrypt_button, 2, 0, 1, 3)
        layout.addWidget(decrypt_button, 3, 0, 1, 3)
        layout.setRowStretch(4, 1)
        self.tabs.addTab(tab_crypto, t('gui_tab_crypto'))
        self.browse_button = browse_button
        self.encrypt_button = encrypt_button
        self.decrypt_button = decrypt_button

    def _create_tools_tab(self):
        tab_tools = QWidget()
        layout = QVBoxLayout(tab_tools)
        tools_tabs = QTabWidget()

        # Hash Calculator
        hash_widget = QWidget()
        hash_layout = QGridLayout(hash_widget)
        self.hash_input = QLineEdit(placeholderText=t('gui_hash_input'))
        self.hash_browse_button = QPushButton(t('gui_hash_select'))
        self.hash_calc_button = QPushButton(t('gui_hash_calc'))
        self.hash_md5_out = QLineEdit(readOnly=True)
        self.hash_sha1_out = QLineEdit(readOnly=True)
        self.hash_sha256_out = QLineEdit(readOnly=True)
        hash_layout.addWidget(QLabel(t('gui_hash_input')), 0, 0)
        hash_layout.addWidget(self.hash_input, 0, 1)
        hash_layout.addWidget(self.hash_browse_button, 0, 2)
        hash_layout.addWidget(self.hash_calc_button, 1, 0, 1, 3)
        hash_layout.addWidget(QLabel("MD5:"), 2, 0)
        hash_layout.addWidget(self.hash_md5_out, 2, 1, 1, 2)
        hash_layout.addWidget(QLabel("SHA1:"), 3, 0)
        hash_layout.addWidget(self.hash_sha1_out, 3, 1, 1, 2)
        hash_layout.addWidget(QLabel("SHA256:"), 4, 0)
        hash_layout.addWidget(self.hash_sha256_out, 4, 1, 1, 2)
        tools_tabs.addTab(hash_widget, "Hash")

        # QR Code Generator
        qr_widget = QWidget()
        qr_layout = QVBoxLayout(qr_widget)
        self.qr_input = QLineEdit(placeholderText=t('gui_qr_input'))
        self.qr_generate_button = QPushButton(t('gui_qr_gen'))
        self.qr_image_label = QLabel("QR Code Preview")
        self.qr_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_image_label.setFixedSize(250, 250)
        self.qr_image_label.setStyleSheet("border: 1px solid #ccc; background-color: white;")
        self.qr_save_button = QPushButton(t('gui_qr_save'))
        qr_layout.addWidget(self.qr_input)
        qr_layout.addWidget(self.qr_generate_button)
        qr_layout.addWidget(self.qr_image_label, alignment=Qt.AlignmentFlag.AlignCenter)
        qr_layout.addWidget(self.qr_save_button)
        tools_tabs.addTab(qr_widget, "QR")

        # Random Password
        pass_widget = QWidget()
        pass_layout = QVBoxLayout(pass_widget)
        pass_options_layout = QHBoxLayout()
        pass_options_layout.addWidget(QLabel(t('gui_pass_count')))
        self.pass_count_spin = QSpinBox(minimum=1, maximum=100, value=10)
        self.pass_generate_button = QPushButton(t('gui_pass_gen'))
        self.pass_save_button = QPushButton(t('gui_pass_save'))
        pass_options_layout.addWidget(self.pass_count_spin)
        pass_options_layout.addWidget(self.pass_generate_button)
        pass_options_layout.addWidget(self.pass_save_button)
        self.pass_output = QTextEdit(readOnly=True)
        pass_layout.addLayout(pass_options_layout)
        pass_layout.addWidget(self.pass_output)
        tools_tabs.addTab(pass_widget, "Password")

        layout.addWidget(tools_tabs)
        self.tabs.addTab(tab_tools, t('gui_tab_tools'))

    def _create_settings_tab(self):
        tab_settings = QWidget()
        layout = QGridLayout(tab_settings)
        layout.addWidget(QLabel(t('gui_api_keys')), 0, 0, 1, 2)
        self.deepseek_key_input = QLineEdit(echoMode=QLineEdit.EchoMode.Password, text=deepseek_api_key)
        self.gemini_key_input = QLineEdit(echoMode=QLineEdit.EchoMode.Password, text=gemini_api_key)
        self.save_keys_button = QPushButton(t('gui_save_keys'))
        layout.addWidget(QLabel("DeepSeek Key:"), 1, 0)
        layout.addWidget(self.deepseek_key_input, 1, 1)
        layout.addWidget(QLabel("Gemini Key:"), 2, 0)
        layout.addWidget(self.gemini_key_input, 2, 1)
        layout.addWidget(self.save_keys_button, 3, 0, 1, 2)

        layout.addWidget(QLabel(t('gui_security')), 4, 0, 1, 2)
        self.change_password_button = QPushButton(t('gui_change_key_btn'))
        layout.addWidget(self.change_password_button, 5, 0, 1, 2)

        layout.addWidget(QLabel(t('gui_proxy')), 6, 0, 1, 2)
        self.proxy_input = QLineEdit(placeholderText="e.g. http://127.0.0.1:7890")
        self.set_proxy_button = QPushButton(t('gui_set_proxy'))
        self.clear_proxy_button = QPushButton(t('gui_clear_proxy'))
        proxy_layout = QHBoxLayout()
        proxy_layout.addWidget(self.proxy_input)
        proxy_layout.addWidget(self.set_proxy_button)
        proxy_layout.addWidget(self.clear_proxy_button)
        layout.addLayout(proxy_layout, 7, 0, 1, 2)

        # Language Selection
        layout.addWidget(QLabel(t('gui_lang_header')), 8, 0, 1, 2)
        self.lang_combo = QComboBox()
        self.lang_codes = list(i18n.LANGUAGES.keys())
        for code in self.lang_codes:
            self.lang_combo.addItem(i18n.LANGUAGES[code])

        # Set current selection
        try:
            current_index = self.lang_codes.index(i18n.current_language)
            self.lang_combo.setCurrentIndex(current_index)
        except ValueError:
            pass

        self.lang_combo.currentIndexChanged.connect(self.change_language)
        layout.addWidget(self.lang_combo, 9, 0, 1, 2)

        layout.addWidget(QLabel(t('gui_updates')), 10, 0, 1, 2)
        self.check_update_button = QPushButton(t('gui_check_update'))
        layout.addWidget(self.check_update_button, 11, 0, 1, 2)

        self.about_button = QPushButton(t('gui_about'))
        layout.addWidget(self.about_button, 12, 0, 1, 2)

        layout.setRowStretch(13, 1)
        self.tabs.addTab(tab_settings, t('gui_tab_settings'))

    def _connect_signals(self):
        # AI Tab
        self.ai_send_button.clicked.connect(self.send_ai_message)
        self.ai_input.returnPressed.connect(self.send_ai_message)
        # Crypto Tab
        self.browse_button.clicked.connect(self.browse_file)
        self.encrypt_button.clicked.connect(lambda: self.start_crypto('encrypt'))
        self.decrypt_button.clicked.connect(lambda: self.start_crypto('decrypt'))
        # Tools Tab
        self.hash_browse_button.clicked.connect(self.browse_hash_file)
        self.hash_calc_button.clicked.connect(self.calculate_hash)
        self.qr_generate_button.clicked.connect(self.generate_qrcode)
        self.qr_save_button.clicked.connect(self.save_qrcode)
        self.pass_generate_button.clicked.connect(self.generate_passwords)
        self.pass_save_button.clicked.connect(self.save_passwords)
        # Settings Tab
        self.save_keys_button.clicked.connect(self.save_api_keys)
        self.change_password_button.clicked.connect(self.change_password)
        self.set_proxy_button.clicked.connect(self.set_proxy)
        self.clear_proxy_button.clicked.connect(self.clear_proxy)
        self.check_update_button.clicked.connect(self.check_for_updates_manual)
        self.about_button.clicked.connect(self.show_about_dialog)

    def change_language(self, index):
        new_lang = self.lang_codes[index]
        if new_lang != i18n.current_language:
            i18n.save_language(new_lang)
            QMessageBox.information(self, "Language Changed", t('gui_restart_msg'))

    def show_about_dialog(self):
        dialog = AboutDialog(self)
        dialog.exec()

    def check_for_updates_auto_silent(self):
        updater.check_for_updates(CURRENT_VERSION, "falcon_gui", parent_widget=self, silent=True)

    def check_for_updates_manual(self):
        self.status_bar.setText(t('checking_updates'))
        updater.check_for_updates(CURRENT_VERSION, "falcon_gui", parent_widget=self)
        self.status_bar.setText(t('gui_ready'))

    def send_ai_message(self):
        prompt = self.ai_input.text().strip()
        if not prompt or (self.ai_worker and self.ai_worker.isRunning()): return

        selected_model_name = self.ai_model_combo.currentText()
        model_info = self.ai_models[selected_model_name]
        api_key = deepseek_api_key if model_info['type'] == 'deepseek' else gemini_api_key

        if not api_key:
            QMessageBox.warning(self, "Missing API Key", t('ai_no_keys'))
            return

        self.ai_input.clear()
        self.ai_history.append(f"<b style='color:#00aaff;'>You:</b> {prompt}<br>")
        self.ai_history.append(f"<b style='color:#aaff00;'>{selected_model_name}:</b> ")
        self.ai_send_button.setEnabled(False)
        self.status_bar.setText(f"Requesting {selected_model_name}...")

        self.ai_worker = AIWorker(prompt, model_info, api_key)
        self.ai_worker.new_token.connect(self._append_ai_token)
        self.ai_worker.finished.connect(self.ai_message_finished)
        self.ai_worker.error.connect(self.ai_message_error)
        self.ai_worker.start()

    def _append_ai_token(self, token):
        self.ai_history.moveCursor(QTextCursor.MoveOperation.End)
        self.ai_history.insertPlainText(token)
        self.ai_history.moveCursor(QTextCursor.MoveOperation.End)

    def ai_message_finished(self):
        self.ai_history.append("<br>")
        self.ai_send_button.setEnabled(True)
        self.status_bar.setText(t('gui_ready'))
        self.ai_input.setFocus()

    def ai_message_error(self, error_msg):
        self.ai_history.append(f"<p style='color:red;'>{error_msg}</p><br>")
        self.ai_message_finished()

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file_path: self.crypto_file_path.setText(file_path)

    def start_crypto(self, mode):
        file_path = self.crypto_file_path.text()
        password = self.crypto_password.text()
        if not file_path or not password:
            QMessageBox.warning(self, "Incomplete", "Please select a file and enter a password.")
            return

        reply = QMessageBox.question(self, "Confirm", "Original file will be deleted. Continue?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.status_bar.setText(f"{'Encrypting' if mode == 'encrypt' else 'Decrypting'} file...")
            self.crypto_worker = CryptoWorker(file_path, password, mode)
            self.crypto_worker.finished.connect(self.crypto_finished)
            self.crypto_worker.start()

    def crypto_finished(self, success, message):
        if success:
            QMessageBox.information(self, "Success", message)
            self.crypto_file_path.clear()
            self.crypto_password.clear()
        else:
            QMessageBox.critical(self, "Failed", message)
        self.status_bar.setText(t('gui_ready'))

    def browse_hash_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file_path: self.hash_input.setText(file_path)

    def calculate_hash(self):
        text = self.hash_input.text()
        if not text: return
        if os.path.exists(text):
            try:
                md5, sha1, sha256 = hashlib.md5(), hashlib.sha1(), hashlib.sha256()
                with open(text, 'rb') as f:
                    while chunk := f.read(8192):
                        md5.update(chunk); sha1.update(chunk); sha256.update(chunk)
                self.hash_md5_out.setText(md5.hexdigest())
                self.hash_sha1_out.setText(sha1.hexdigest())
                self.hash_sha256_out.setText(sha256.hexdigest())
            except Exception as e: QMessageBox.critical(self, "Error", f"Read failed: {e}")
        else:
            encoded_text = text.encode('utf-8')
            self.hash_md5_out.setText(hashlib.md5(encoded_text).hexdigest())
            self.hash_sha1_out.setText(hashlib.sha1(encoded_text).hexdigest())
            self.hash_sha256_out.setText(hashlib.sha256(encoded_text).hexdigest())

    def generate_qrcode(self):
        data = self.qr_input.text()
        if not data: return
        try:
            img = qrcode.make(data)
            pil_img = img.convert("RGBA")
            qimage = QImage(pil_img.tobytes("raw", "RGBA"), pil_img.size[0], pil_img.size[1], QImage.Format.Format_RGBA8888)
            self.qr_pixmap = QPixmap.fromImage(qimage)
            self.qr_image_label.setPixmap(self.qr_pixmap.scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio))
        except Exception as e: QMessageBox.critical(self, "Error", f"QR Generation Failed: {e}")

    def save_qrcode(self):
        if not self.qr_pixmap:
            QMessageBox.warning(self, "Empty", "Generate a QR code first.")
            return

        save_path, _ = QFileDialog.getSaveFileName(self, "Save QR", DOCUMENTS_PATH, "PNG Files (*.png)")
        if save_path:
            self.qr_pixmap.save(save_path, "PNG")
            self.status_bar.setText(f"Saved to {save_path}")

    def generate_passwords(self):
        count = self.pass_count_spin.value()
        passwords = misc.generate_random_passwords(count)[:count]
        self.pass_output.setText("\n".join(passwords))

    def save_passwords(self):
        content = self.pass_output.toPlainText()
        if not content:
            QMessageBox.warning(self, "Empty", "Generate passwords first.")
            return

        save_path, _ = QFileDialog.getSaveFileName(self, "Save Passwords", DOCUMENTS_PATH, "Text Files (*.txt)")
        if save_path:
            try:
                with open(save_path, 'w', encoding='utf-8') as f:
                    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                    f.write(f"--- FALCON OS Passwords ---\n")
                    f.write(f"Time: {timestamp}\n")
                    f.write("--------------------------------\n\n")
                    f.write(content)
                self.status_bar.setText(f"Saved to: {save_path}")
            except Exception as e:
                QMessageBox.critical(self, "Failed", f"Write error: {e}")

    def save_api_keys(self):
        global deepseek_api_key, gemini_api_key
        deepseek_api_key = self.deepseek_key_input.text()
        gemini_api_key = self.gemini_key_input.text()
        security.save_api_keys(deepseek_api_key, gemini_api_key)
        QMessageBox.information(self, "Success", t('saved'))

    def change_password(self):
        dialog = SetPasswordDialog(self)
        dialog.exec()

    def set_proxy(self):
        proxy = self.proxy_input.text().strip()
        if proxy:
            os.environ['HTTP_PROXY'] = proxy
            os.environ['HTTPS_PROXY'] = proxy
            self.status_bar.setText(t('proxy_set', proxy))
        else:
            QMessageBox.warning(self, "Error", "Proxy address empty.")

    def clear_proxy(self):
        os.environ.pop('HTTP_PROXY', None)
        os.environ.pop('HTTPS_PROXY', None)
        self.proxy_input.clear()
        self.status_bar.setText(t('proxy_cleared'))


# --- Main Application Entry Point ---
def run():
    global deepseek_api_key, gemini_api_key, user_password, security_questions
    deepseek_api_key, gemini_api_key = security.load_api_keys()
    user_password, security_questions = security.load_credentials()

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLESHEET)
    app.setFont(QFont("Segoe UI", 10))

    splash = SplashScreen()
    splash.show()

    # Fake loading
    for i in range(1, 11):
        # Translate the splash message dynamically
        splash.show_message(t('gui_core_load', i))
        app.processEvents()
        time.sleep(0.05)

    login_win = LoginWindow()
    splash.finish(login_win)

    if login_win.exec():
        main_win = MainWindow()
        main_win.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)

if __name__ == '__main__':
    run()