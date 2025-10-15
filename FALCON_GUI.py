# FALCON_GUI.py (Version 2.1 - SyntaxError Fixed & Fully Integrated)
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
                             QSplashScreen)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QIcon, QPixmap, QImage, QFont, QTextCursor, QPainter

# Import your existing logic modules
import FALCON_jd
import FALCON_crypto
import DCai
import DCai_Gemini
import FALCON_updater # 导入新的更新模块
from openai import OpenAI, AuthenticationError
import google.generativeai as genai

def resource_path(relative_path):
    """ 获取资源的绝对路径，适用于开发环境和 PyInstaller 打包环境 """
    try:
        # PyInstaller 创建一个临时文件夹并将路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- Global Variables and Constants ---
CURRENT_VERSION = "2.4.9 GUI"
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
                client = OpenAI(api_key=self.api_key, base_url=DCai.BASE_URL)
                response = client.chat.completions.create(
                    model=DCai.MODEL_NAME, messages=[{"role": "user", "content": self.prompt}], stream=True
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
            self.error.emit("API 请求失败: API 密钥无效或已过期，请在设置中检查。")
        except Exception as e:
            error_message = str(e)
            if "API key" in error_message:
                self.error.emit("API 请求失败: API 密钥无效或已过期，请在设置中检查。")
            else:
                self.error.emit(f"API 请求失败: {e}")
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
        __builtins__.input = lambda _: 'y'
        try:
            if self.mode == 'encrypt':
                result = FALCON_crypto.encrypt_file(self.file_path, self.password)
                if result: self.finished.emit(True, f"文件已成功加密为 {self.file_path}.enc")
                else: self.finished.emit(False, "加密失败，请查看控制台输出。")
            elif self.mode == 'decrypt':
                result = FALCON_crypto.decrypt_file(self.file_path, self.password)
                if result: self.finished.emit(True, f"文件已成功解密为 {self.file_path.replace('.enc', '')}")
                else: self.finished.emit(False, "解密失败，请查看控制台输出。")
        except Exception as e:
            self.finished.emit(False, f"发生错误: {e}")
        finally:
            __builtins__.input = original_input

# --- GUI Windows ---

class SplashScreen(QSplashScreen):
    def __init__(self):
        original_pixmap = QPixmap(resource_path("logo.png"))
        text_margin = 50
        new_width = original_pixmap.width()
        new_height = original_pixmap.height() + text_margin
        composite_pixmap = QPixmap(new_width, new_height)
        composite_pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(composite_pixmap)
        painter.drawPixmap(0, 0, original_pixmap)  # 在左上角 (0, 0) 位置绘制
        painter.end()
        super().__init__(composite_pixmap)

        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.showMessage("正在初始化FALCON OS...",
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
        self.setWindowTitle("设置新的软件密钥")
        self.setMinimumWidth(450)
        self.layout = QGridLayout(self)

        self.current_pass = QLineEdit(echoMode=QLineEdit.EchoMode.Password)
        self.new_pass = QLineEdit(echoMode=QLineEdit.EchoMode.Password)
        self.confirm_pass = QLineEdit(echoMode=QLineEdit.EchoMode.Password)

        self.q1 = QLineEdit(placeholderText="自定义问题 1")
        self.a1 = QLineEdit(placeholderText="问题 1 的答案")
        self.q2 = QLineEdit(placeholderText="自定义问题 2")
        self.a2 = QLineEdit(placeholderText="问题 2 的答案")
        self.q3 = QLineEdit(placeholderText="自定义问题 3")
        self.a3 = QLineEdit(placeholderText="问题 3 的答案")

        self.save_button = QPushButton("💾 保存设置")

        self.layout.addWidget(QLabel("当前密钥:"), 0, 0)
        self.layout.addWidget(self.current_pass, 0, 1)
        self.layout.addWidget(QLabel("新密钥:"), 1, 0)
        self.layout.addWidget(self.new_pass, 1, 1)
        self.layout.addWidget(QLabel("确认新密钥:"), 2, 0)
        self.layout.addWidget(self.confirm_pass, 2, 1)

        self.layout.addWidget(QLabel("<b>密保问题 (用于找回密钥):</b>"), 3, 0, 1, 2)
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
            QMessageBox.warning(self, "验证失败", "当前密钥不正确。")
            return

        if not self.new_pass.text() or self.new_pass.text() != self.confirm_pass.text():
            QMessageBox.warning(self, "错误", "新密钥为空或两次输入不匹配。")
            return

        questions = {
            self.q1.text().strip(): self.a1.text().strip(),
            self.q2.text().strip(): self.a2.text().strip(),
            self.q3.text().strip(): self.a3.text().strip(),
        }
        if any(not q or not a for q, a in questions.items()):
            QMessageBox.warning(self, "错误", "所有密保问题和答案都必须填写。")
            return

        FALCON_jd.save_credentials(self.new_pass.text(), questions)
        user_password = self.new_pass.text()
        security_questions = questions

        QMessageBox.information(self, "成功", "新密钥和密保问题已设置成功！")
        self.accept()

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FALCON OS - 身份验证")
        self.setWindowIcon(QIcon(resource_path("favicon.ico")))  # FIX: Icon restored
        self.setFixedSize(350, 150)
        self.attempts_left = 3
        self.active_password = user_password if user_password else "114514"
        layout = QVBoxLayout(self)
        self.password_input = QLineEdit(echoMode=QLineEdit.EchoMode.Password, placeholderText="请输入密钥")
        login_button = QPushButton("✔️ 验证")
        forgot_button = QPushButton("❓ 忘记密钥")
        layout.addWidget(QLabel("请输入访问密钥:"))
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
                QMessageBox.warning(self, "错误", f"密钥错误，您还有 {self.attempts_left} 次机会。")
            else:
                QMessageBox.critical(self, "访问被拒绝", "密钥错误次数过多，程序将退出。")
                self.reject()

    def forgot_password(self):
        if not user_password or not security_questions:
            QMessageBox.warning(self, "无法重置", "未设置用户密码和密保问题，无法找回。")
            return

        question = random.choice(list(security_questions.keys()))
        answer, ok = QInputDialog.getText(self, "密保问题", f"请回答以下问题以重置密钥:\n\n{question}")

        if ok and answer and answer.strip() == security_questions[question]:
            new_password, ok = QInputDialog.getText(self, "重置密钥", "验证成功，请输入您的新密钥:", QLineEdit.EchoMode.Password)
            if ok and new_password:
                confirm_password, ok = QInputDialog.getText(self, "确认密钥", "请再次输入以确认:", QLineEdit.EchoMode.Password)
                if ok and new_password == confirm_password:
                    FALCON_jd.save_credentials(new_password, security_questions)
                    QMessageBox.information(self, "成功", "密钥已重置！请重新启动程序并使用新密钥登录。")
                    self.reject()
                else:
                    QMessageBox.warning(self, "错误", "两次输入的密钥不匹配。")
        else:
            QMessageBox.critical(self, "失败", "答案错误，重置失败。")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"FALCON OS v{CURRENT_VERSION}")
        self.setWindowIcon(QIcon(resource_path("favicon.ico"))) # fix icon restored
        self.setGeometry(100, 100, 950, 750)
        self.ai_worker = None
        self.crypto_worker = None
        self.qr_pixmap = None
        self._init_ui()

        # 在主窗口加载后，启动一个延时、静默的自动更新检查
        QTimer.singleShot(1500, self.check_for_updates_auto_silent)

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        self._create_tabs()
        main_layout.addWidget(self.tabs)
        self.status_bar = QLabel("准备就绪。")
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
        model_layout.addWidget(QLabel("选择AI模型:"))
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
        self.ai_input = QLineEdit(placeholderText="在这里输入您的问题... (Enter 发送)")
        self.ai_send_button = QPushButton("➤ 发送")
        input_layout.addWidget(self.ai_input)
        input_layout.addWidget(self.ai_send_button)
        layout.addLayout(input_layout)
        self.tabs.addTab(tab_ai, "💬 AI 对话")

    def _create_crypto_tab(self):
        tab_crypto = QWidget()
        layout = QGridLayout(tab_crypto)
        self.crypto_file_path = QLineEdit(placeholderText="点击右侧按钮选择文件", readOnly=True)
        browse_button = QPushButton("📂 浏览...")
        self.crypto_password = QLineEdit(echoMode=QLineEdit.EchoMode.Password, placeholderText="输入用于加解密的密码")
        encrypt_button = QPushButton("🔒 加密文件")
        decrypt_button = QPushButton("🔑 解密文件")
        layout.addWidget(QLabel("文件路径:"), 0, 0)
        layout.addWidget(self.crypto_file_path, 0, 1)
        layout.addWidget(browse_button, 0, 2)
        layout.addWidget(QLabel("密码:"), 1, 0)
        layout.addWidget(self.crypto_password, 1, 1, 1, 2)
        layout.addWidget(encrypt_button, 2, 0, 1, 3)
        layout.addWidget(decrypt_button, 3, 0, 1, 3)
        layout.setRowStretch(4, 1)
        self.tabs.addTab(tab_crypto, "🛡️ 文件安全")
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
        self.hash_input = QLineEdit(placeholderText="输入文本或选择文件")
        self.hash_browse_button = QPushButton("📂 选择文件")
        self.hash_calc_button = QPushButton("🧮 计算哈希")
        self.hash_md5_out = QLineEdit(readOnly=True)
        self.hash_sha1_out = QLineEdit(readOnly=True)
        self.hash_sha256_out = QLineEdit(readOnly=True)
        hash_layout.addWidget(QLabel("输入:"), 0, 0)
        hash_layout.addWidget(self.hash_input, 0, 1)
        hash_layout.addWidget(self.hash_browse_button, 0, 2)
        hash_layout.addWidget(self.hash_calc_button, 1, 0, 1, 3)
        hash_layout.addWidget(QLabel("MD5:"), 2, 0)
        hash_layout.addWidget(self.hash_md5_out, 2, 1, 1, 2)
        hash_layout.addWidget(QLabel("SHA1:"), 3, 0)
        hash_layout.addWidget(self.hash_sha1_out, 3, 1, 1, 2)
        hash_layout.addWidget(QLabel("SHA256:"), 4, 0)
        hash_layout.addWidget(self.hash_sha256_out, 4, 1, 1, 2)
        tools_tabs.addTab(hash_widget, "哈希计算器")

        # QR Code Generator
        qr_widget = QWidget()
        qr_layout = QVBoxLayout(qr_widget)
        self.qr_input = QLineEdit(placeholderText="输入要编码的文本或URL")
        self.qr_generate_button = QPushButton("✨ 生成二维码")
        self.qr_image_label = QLabel("二维码将显示在这里")
        self.qr_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_image_label.setFixedSize(250, 250)
        self.qr_image_label.setStyleSheet("border: 1px solid #ccc; background-color: white;")
        self.qr_save_button = QPushButton("💾 保存二维码")
        qr_layout.addWidget(self.qr_input)
        qr_layout.addWidget(self.qr_generate_button)
        qr_layout.addWidget(self.qr_image_label, alignment=Qt.AlignmentFlag.AlignCenter)
        qr_layout.addWidget(self.qr_save_button)
        tools_tabs.addTab(qr_widget, "二维码")

        # Random Password
        pass_widget = QWidget()
        pass_layout = QVBoxLayout(pass_widget)
        pass_options_layout = QHBoxLayout()
        pass_options_layout.addWidget(QLabel("生成数量:"))
        self.pass_count_spin = QSpinBox(minimum=1, maximum=100, value=10)
        self.pass_generate_button = QPushButton("🎲 生成")
        self.pass_save_button = QPushButton("💾 保存为 .txt")
        pass_options_layout.addWidget(self.pass_count_spin)
        pass_options_layout.addWidget(self.pass_generate_button)
        pass_options_layout.addWidget(self.pass_save_button)
        self.pass_output = QTextEdit(readOnly=True)
        pass_layout.addLayout(pass_options_layout)
        pass_layout.addWidget(self.pass_output)
        tools_tabs.addTab(pass_widget, "随机密码")

        layout.addWidget(tools_tabs)
        self.tabs.addTab(tab_tools, "🛠️ 实用工具")

    def _create_settings_tab(self):
        tab_settings = QWidget()
        layout = QGridLayout(tab_settings)
        layout.addWidget(QLabel("<b>API 密钥设置</b>"), 0, 0, 1, 2)
        self.deepseek_key_input = QLineEdit(echoMode=QLineEdit.EchoMode.Password, text=deepseek_api_key)
        self.gemini_key_input = QLineEdit(echoMode=QLineEdit.EchoMode.Password, text=gemini_api_key)
        self.save_keys_button = QPushButton("💾 保存 API 密钥")
        layout.addWidget(QLabel("DeepSeek API Key:"), 1, 0)
        layout.addWidget(self.deepseek_key_input, 1, 1)
        layout.addWidget(QLabel("Gemini API Key:"), 2, 0)
        layout.addWidget(self.gemini_key_input, 2, 1)
        layout.addWidget(self.save_keys_button, 3, 0, 1, 2)

        layout.addWidget(QLabel("<b>修改软件密钥</b>"), 4, 0, 1, 2)
        self.change_password_button = QPushButton("🔑 修改密钥与密保问题")
        layout.addWidget(self.change_password_button, 5, 0, 1, 2)

        layout.addWidget(QLabel("<b>网络代理设置</b>"), 6, 0, 1, 2)
        self.proxy_input = QLineEdit(placeholderText="例如: http://127.0.0.1:7890")
        self.set_proxy_button = QPushButton("✔️ 设置代理")
        self.clear_proxy_button = QPushButton("❌ 清除代理")
        proxy_layout = QHBoxLayout()
        proxy_layout.addWidget(self.proxy_input)
        proxy_layout.addWidget(self.set_proxy_button)
        proxy_layout.addWidget(self.clear_proxy_button)
        layout.addLayout(proxy_layout, 7, 0, 1, 2)

        layout.addWidget(QLabel("<b>检查更新</b>"), 8, 0, 1, 2)
        self.check_update_button = QPushButton("🔄 检查更新")
        layout.addWidget(self.check_update_button, 9, 0, 1, 2)

        layout.setRowStretch(10, 1)
        self.tabs.addTab(tab_settings, "⚙️ 设置")

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

    def check_for_updates_auto_silent(self):
        """启动时自动、静默地检查更新。"""
        # 调用更新器，使用关键字 "falcon_gui"
        FALCON_updater.check_for_updates(CURRENT_VERSION, "falcon_gui", parent_widget=self, silent=True)

    def check_for_updates_manual(self):
        """手动检查更新，会显示弹窗。"""
        self.status_bar.setText("正在检查更新...")
        # 调用更新器，使用关键字 "falcon_gui"
        FALCON_updater.check_for_updates(CURRENT_VERSION, "falcon_gui", parent_widget=self)
        self.status_bar.setText("准备就绪。")

    def send_ai_message(self):
        prompt = self.ai_input.text().strip()
        if not prompt or (self.ai_worker and self.ai_worker.isRunning()): return

        selected_model_name = self.ai_model_combo.currentText()
        model_info = self.ai_models[selected_model_name]
        api_key = deepseek_api_key if model_info['type'] == 'deepseek' else gemini_api_key

        if not api_key:
            QMessageBox.warning(self, "API 密钥缺失", f"{selected_model_name} 的 API 密钥未设置。")
            return

        self.ai_input.clear()
        self.ai_history.append(f"<b style='color:#00aaff;'>您:</b> {prompt}<br>")
        self.ai_history.append(f"<b style='color:#aaff00;'>{selected_model_name}:</b> ")
        self.ai_send_button.setEnabled(False)
        self.status_bar.setText(f"正在向 {selected_model_name} 发送请求...")

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
        self.status_bar.setText("准备就绪。")
        self.ai_input.setFocus()

    def ai_message_error(self, error_msg):
        self.ai_history.append(f"<p style='color:red;'>{error_msg}</p><br>")
        self.ai_message_finished()

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文件")
        if file_path: self.crypto_file_path.setText(file_path)

    def start_crypto(self, mode):
        file_path = self.crypto_file_path.text()
        password = self.crypto_password.text()
        if not file_path or not password:
            QMessageBox.warning(self, "信息不完整", "请选择文件并输入密码。")
            return

        reply = QMessageBox.question(self, "确认操作", "此操作将删除源文件，是否继续?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.status_bar.setText(f"正在{'加密' if mode == 'encrypt' else '解密'}文件...")
            self.crypto_worker = CryptoWorker(file_path, password, mode)
            self.crypto_worker.finished.connect(self.crypto_finished)
            self.crypto_worker.start()

    def crypto_finished(self, success, message):
        if success:
            QMessageBox.information(self, "成功", message)
            self.crypto_file_path.clear()
            self.crypto_password.clear()
        else:
            QMessageBox.critical(self, "失败", message)
        self.status_bar.setText("准备就绪。")

    def browse_hash_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文件计算哈希")
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
            except Exception as e: QMessageBox.critical(self, "错误", f"读取文件失败: {e}")
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
        except Exception as e: QMessageBox.critical(self, "错误", f"生成二维码失败: {e}")

    def save_qrcode(self):
        if not self.qr_pixmap:
            QMessageBox.warning(self, "无内容", "请先生成一个二维码。")
            return

        save_path, _ = QFileDialog.getSaveFileName(self, "保存二维码", DOCUMENTS_PATH, "PNG Files (*.png)")
        if save_path:
            self.qr_pixmap.save(save_path, "PNG")
            self.status_bar.setText(f"二维码已保存至 {save_path}")

    def generate_passwords(self):
        count = self.pass_count_spin.value()
        passwords = FALCON_jd.random16((count + 4) // 5)[:count]
        self.pass_output.setText("\n".join(passwords))

    def save_passwords(self):
        content = self.pass_output.toPlainText()
        if not content:
            QMessageBox.warning(self, "无内容", "请先生成密码。")
            return

        save_path, _ = QFileDialog.getSaveFileName(self, "保存密码", DOCUMENTS_PATH, "Text Files (*.txt)")
        if save_path:
            try:
                with open(save_path, 'w', encoding='utf-8') as f:
                    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                    f.write(f"--- FALCON OS 密码生成记录 ---\n")
                    f.write(f"生成时间: {timestamp}\n")
                    f.write("--------------------------------\n\n")
                    f.write(content)
                self.status_bar.setText(f"密码已保存至: {save_path}")
            except Exception as e:
                QMessageBox.critical(self, "保存失败", f"无法写入文件: {e}")

    def save_api_keys(self):
        global deepseek_api_key, gemini_api_key
        deepseek_api_key = self.deepseek_key_input.text()
        gemini_api_key = self.gemini_key_input.text()
        FALCON_jd.save_api_keys(deepseek_api_key, gemini_api_key)
        QMessageBox.information(self, "成功", "API密钥已加密保存！")

    def change_password(self):
        dialog = SetPasswordDialog(self)
        dialog.exec()

    def set_proxy(self):
        proxy = self.proxy_input.text().strip()
        if proxy:
            os.environ['HTTP_PROXY'] = proxy
            os.environ['HTTPS_PROXY'] = proxy
            self.status_bar.setText(f"代理已设置为: {proxy}")
        else:
            QMessageBox.warning(self, "错误", "代理地址不能为空。")

    def clear_proxy(self):
        os.environ.pop('HTTP_PROXY', None)
        os.environ.pop('HTTPS_PROXY', None)
        self.proxy_input.clear()
        self.status_bar.setText("代理已清除。")


# --- Main Application Entry Point ---
if __name__ == '__main__':
    deepseek_api_key, gemini_api_key = FALCON_jd.load_api_keys()
    user_password, security_questions = FALCON_jd.load_credentials()

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLESHEET)
    app.setFont(QFont("Segoe UI", 10))

    splash = SplashScreen()
    splash.show()

    loading_steps = [f"正在启动核心H{i}" for i in range(1, 11)] + [f"正在检查核心H{i}状态" for i in range(1, 11)] + ["所有核心运行正常"]
    for step in loading_steps:
        splash.show_message(step)
        app.processEvents()
        time.sleep(0.08)

    # 移除这里的更新检查，将其移至 MainWindow
    # splash.update_message("正在检查更新...")
    # app.processEvents()
    # FALCON_updater.check_for_updates(CURRENT_VERSION, "FALCON_OS.exe", parent_widget=None, silent=True)


    login_win = LoginWindow()
    splash.finish(login_win)

    if login_win.exec():
        main_win = MainWindow()
        main_win.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)