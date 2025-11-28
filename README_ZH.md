# FALCON OS: 您的安全命令行与图形界面伴侣

[English](README.md) | [简体中文](README_ZH.md)

FALCON OS 是一款功能强大、注重安全的多平台应用程序，它提供了两种截然不同的使用体验：一个为效率而生的**命令行界面 (CLI)** 和一个为便捷而生的**图形用户界面 (GUI)**。FALCON 的核心使命是为您提供流畅、安全的 AI 聊天体验，它深度集成了业界领先的 **DeepSeek** 和 **Google Gemini** 大语言模型。我们始终将您的隐私放在首位，确保您的 API 密钥和登录凭证等敏感数据，通过高强度加密算法，安全地存储在您的本地设备上。

## ✨ 核心亮点

* **双界面设计**：您可以根据自己的喜好和需求，在经典的命令行界面（CLI）和使用 PyQt6 构建的现代化图形界面（GUI）之间自由选择。
* **双 AI 引擎**：无缝集成并切换使用 DeepSeek 和 Google Gemini 的强大语言模型。
* **金融级安全**：采用高强度的 **AES-GCM 加密算法**，结合本地随机密钥与程序内部密钥（Pepper）的双重保护机制。
* **完善的用户认证**：内置完整的登录验证系统。默认密钥为 `114514`。可通过密保问题重置。
* **自动更新**：内置更新检查功能，连接到 GitHub 检查最新版本。
* **强大的集成工具箱**：
  * **文件加密/解密**：安全地加密或解密您的本地文件。
  * **哈希计算器**：计算 MD5, SHA-1, SHA-256。
  * **二维码生成器**：生成并保存二维码。
  * **随机密码生成**：生成高强度随机密码。
  * **系统资源监控**：查看 CPU 和内存使用率。
  * **网络代理设置**：配置 HTTP 代理以访问 Gemini。

## 🚀 快速开始

### 方式一：从源码运行

1. **环境准备**: Python 3.8 或更高版本。
2. **克隆仓库**:
   ```bash
   git clone https://github.com/xiaoyu1738/smaiclub_software_falconos
   cd smaiclub_software_falconos
   ```
3. **安装依赖**:
   ```bash
   pip install -r requirements.txt
   ```
4. **运行**:
   * CLI: `python run_cli.py`
   * GUI: `python run_gui.py`

### 方式二：二进制发行版
请前往 [Releases 页面](https://github.com/xiaoyu1738/smaiclub_software_falconos/releases) 下载。

## 📖 使用指南

1. **首次登录**: 默认密钥为 `114514`。
2. **初始设置**:
   * 使用 `setpassword` (CLI) 或在设置选项卡 (GUI) 中修改密钥并设置密保问题。
   * 使用 `setapikey` (CLI) 或在设置选项卡 (GUI) 中保存您的 DeepSeek/Gemini API 密钥。

## 🔒 安全说明
* 凭证和 API 密钥**绝不会以明文形式存储**。
* **AES-GCM** 确保机密性和完整性。

## 📄 许可证
GNU GPLv3。详情请参阅 `LICENSE` 文件。

---
© 2025 SMAICLUB, FALCON STUDIO. All rights reserved.
