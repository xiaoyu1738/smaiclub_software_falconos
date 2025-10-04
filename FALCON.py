import os
import time
import random

from colorama import Fore, Style  # 导入colorama用于设置不同颜色

import DCai
import DCai_Gemini  # 导入新的Gemini模块
import FALCON_jd
import FALCON_logo

h1 = "[身份验证]>>>>> "
h2 = "[系统]>>>>> "
h3 = "[命令行]>>>>> "
h4 = "[时间]>>>>> "
h5_deepseek = f"{Fore.BLUE}AI(DeepSeek)>>>>>> {Style.RESET_ALL}"

# --- 全局变量 ---
current_proxy = "无"
deepseek_api_key = None
gemini_api_key = None
user_password = None
security_questions = None


def load_all_data():
    """加载所有加密数据，包括API密钥和用户凭证。"""
    global deepseek_api_key, gemini_api_key, user_password, security_questions
    deepseek_api_key, gemini_api_key = FALCON_jd.load_api_keys()
    user_password, security_questions = FALCON_jd.load_credentials()


def start1():
    """处理用户登录、密码验证和找回密码的逻辑。"""
    active_password = user_password if user_password else "114514"
    password_num = 3

    while password_num > 0:
        password_input = input(f"{h1}请输入密钥: ")
        print(f"{h1}验证密钥中...")
        time.sleep(0.35)

        if password_input == active_password:
            print(f"{h1}密钥正确")
            return  # 验证成功，直接返回，继续执行程序
        else:
            password_num -= 1
            if password_num > 0:
                print(f"{h1}{Fore.RED}密钥错误，请重新输入。您还有 {password_num} 次机会。{Style.RESET_ALL}")
            else:
                print(f"{h1}{Fore.RED}密钥错误次数过多。{Style.RESET_ALL}")

    # 添加修改:
    print(f"{h2}您的访问被拒绝")
    FALCON_logo.SB_logo()
    # 结束修改

    # --- 密码输错3次后的逻辑 ---
    # 只有在用户设置了自定义密码和密保问题后，才提供找回功能
    if user_password and security_questions:
        forgot_choice = input(f"{h1}您是否忘记了密钥？(输入 y 重置，任意其他键退出): ").lower()
        if forgot_choice == 'y':
            print(f"{h2}启动密钥重置程序...")

            # 随机选择一个问题来提问
            question = random.choice(list(security_questions.keys()))
            correct_answer = security_questions[question]

            user_answer = input(f"{h1}[密保问题]: {question}\n{h1}请输入您的答案: ")

            if user_answer == correct_answer:
                print(f"{h2}{Fore.GREEN}验证成功！现在请设置您的新密钥。{Style.RESET_ALL}")

                # --- 设置新密钥的逻辑 ---
                while True:
                    new_password = input(f"{h1}请输入您的新密钥: ")
                    confirm_password = input(f"{h1}请再次输入以确认: ")
                    if new_password == confirm_password:
                        if new_password:
                            break
                        else:
                            print(f"{h1}{Fore.RED}密钥不能为空，请重新输入。{Style.RESET_ALL}")
                    else:
                        print(f"{h1}{Fore.RED}两次输入的密钥不匹配，请重新输入。{Style.RESET_ALL}")

                # 使用新密码和旧的密保问题保存凭证
                FALCON_jd.save_credentials(new_password, security_questions)

                print(f"\n{h2}{Fore.GREEN}您的密钥已成功重置！{Style.RESET_ALL}")
                print(f"{h2}请重新启动程序并使用新密钥登录。")

            else:
                # 密保问题回答错误
                print(f"{h2}{Fore.RED}答案错误，重置失败。{Style.RESET_ALL}")

    # 所有失败路径（包括不重置、重置失败等）最终都会执行退出
    os._exit(0)


def start2():
    FALCON_jd.jdt1("正在尝试连接 ", 0.01)
    print("")
    FALCON_jd.jdt1("正在发送请求 ", 0.001)
    print("")
    FALCON_jd.jdt1("正在启动核心H1 ", 0.001)
    print("")
    FALCON_jd.jdt1("正在启动核心H2 ", 0.001)
    print("")
    FALCON_jd.jdt1("正在启动核心H3 ", 0.002)
    print("")
    FALCON_jd.jdt1("正在启动核心H4 ", 0.005)
    print("")
    FALCON_jd.jdt1("正在启动核心H5 ", 0.001)
    print("")
    FALCON_jd.jdt1("正在启动核心H6 ", 0.001)
    print("")
    FALCON_jd.jdt1("正在启动核心H7 ", 0.001)
    print("")
    FALCON_jd.jdt1("正在启动核心H8 ", 0.002)
    print("")
    FALCON_jd.jdt1("正在启动核心H9 ", 0.001)
    print("")
    FALCON_jd.jdt1("正在启动核心H10 ", 0.003)
    print("")
    FALCON_jd.jdt1("正在启动核心H11 ", 0.0001)
    print("")
    FALCON_jd.jdt1("正在启动核心H12 ", 0.002)
    print("")
    FALCON_jd.jdt1("正在启动核心H13 ", 0.001)
    print("")
    FALCON_jd.jdt1("正在启动核心H14 ", 0.001)
    print("")
    FALCON_jd.jdt1("正在启动核心H15 ", 0.0001)
    print("")
    FALCON_jd.jdt1("正在启动核心H16 ", 0.001)
    print("")
    FALCON_jd.jdt1("正在启动核心H17 ", 0.001)
    print("")
    FALCON_jd.jdt1("正在启动核心H18 ", 0.001)
    print("")
    FALCON_jd.jdt1("正在启动核心H19 ", 0.002)
    print("")
    FALCON_jd.jdt1("正在启动核心H20 ", 0.0005)
    print("")
    FALCON_jd.jdt1("正在启动核心H21 ", 0.001)
    print("")
    FALCON_jd.jdt1("正在启动核心H22 ", 0.001)
    print("")
    FALCON_jd.jdt1("正在启动核心H23 ", 0.001)
    print("")
    FALCON_jd.jdt1("正在启动核心H24 ", 0.002)
    print("")
    FALCON_jd.jdt1("正在启动核心H25 ", 0.001)
    print("")
    FALCON_jd.jdt1("正在启动核心H26 ", 0.003)
    print("")
    FALCON_jd.jdt1("正在启动核心H27 ", 0.005)
    print("")
    FALCON_jd.jdt1("正在启动核心H28 ", 0.002)
    print("")
    FALCON_jd.jdt1("正在启动核心H29 ", 0.001)
    print("")
    FALCON_jd.jdt1("正在启动核心H30 ", 0.005)
    print("")
    FALCON_jd.jdt1("正在启动核心H31 ", 0.001)
    print("")
    FALCON_jd.jdt1("正在启动核心H32 ", 0.001)
    print("")

    FALCON_jd.jdt1("正在检查核心H1状态 ", 0.0001)
    print("")
    FALCON_jd.jdt1("正在检查核心H2状态 ", 0.0001)
    print("")
    FALCON_jd.jdt1("正在检查核心H3状态 ", 0.0001)
    print("")
    FALCON_jd.jdt1("正在检查核心H4状态 ", 0.0001)
    print("")
    FALCON_jd.jdt1("正在检查核心H5状态 ", 0.0001)
    print("")
    FALCON_jd.jdt1("正在检查核心H6状态 ", 0.0001)
    print("")
    FALCON_jd.jdt1("正在检查核心H7状态 ", 0.0001)
    print("")
    FALCON_jd.jdt1("正在检查核心H8状态 ", 0.0001)
    print("")
    FALCON_jd.jdt1("正在检查核心H9状态 ", 0.0001)
    print("")
    FALCON_jd.jdt1("正在检查核心H10状态 ", 0.0001)
    print("")
    FALCON_jd.jdt1("正在检查核心H11状态 ", 0.0001)
    print("")
    FALCON_jd.jdt1("正在检查核心H12状态 ", 0.0001)
    print("")
    FALCON_jd.jdt1("正在检查核心H13状态 ", 0.0001)
    print("")
    FALCON_jd.jdt1("正在检查核心H14状态 ", 0.0001)
    print("")
    FALCON_jd.jdt1("正在检查核心H15状态 ", 0.0001)
    print("")
    FALCON_jd.jdt1("正在检查核心H16状态 ", 0.0001)
    print("")
    FALCON_jd.jdt1("正在检查核心H17状态 ", 0.0001)
    print("")
    FALCON_jd.jdt1("正在检查核心H18状态 ", 0.0001)
    print("")
    FALCON_jd.jdt1("正在检查核心H19状态 ", 0.0001)
    print("")
    FALCON_jd.jdt1("正在检查核心H20状态 ", 0.0001)
    print("")
    FALCON_jd.jdt1("正在检查核心H21状态 ", 0.0001)
    print("")
    FALCON_jd.jdt1("正在检查核心H22状态 ", 0.0001)
    print("")
    FALCON_jd.jdt1("正在检查核心H23状态 ", 0.0001)
    print("")
    FALCON_jd.jdt1("正在检查核心H24状态 ", 0.0001)
    print("")
    FALCON_jd.jdt1("正在检查核心H25状态 ", 0.0001)
    print("")
    FALCON_jd.jdt1("正在检查核心H26状态 ", 0.0001)
    print("")
    FALCON_jd.jdt1("正在检查核心H27状态 ", 0.0001)
    print("")
    FALCON_jd.jdt1("正在检查核心H28状态 ", 0.0001)
    print("")
    FALCON_jd.jdt1("正在检查核心H29状态 ", 0.0001)
    print("")
    FALCON_jd.jdt1("正在检查核心H30状态 ", 0.0001)
    print("")
    FALCON_jd.jdt1("正在检查核心H31状态 ", 0.0001)
    print("")
    FALCON_jd.jdt1("正在检查核心H32状态 ", 0.0001)
    print("")

    time.sleep(0.5)
    print(f"{h2}核心运行中")
    time.sleep(0.2)
    print(f"{h2}连接正常")
    time.sleep(0.2)
    FALCON_jd.jdt1("正在启动安全程序 ", 0.001)
    print("")
    time.sleep(0.2)
    FALCON_jd.jdt1("正在启动主程序 ", 0.01)
    print("")
    time.sleep(0.5)
    print("")
    print(f"{h2}启动完成 耗时 000分 15秒 12毫秒")
    print("")

    FALCON_logo.SMAICLUB_logo()
    print(f"{h2}系统运行中...")
    print("================================================================================")
    print(f"{h3}命令行已在线,输入help查看可用命令")


def command1():
    while True:
        cmd1 = input(f"{h3}")

        if cmd1 == "help":
            print(f"{h3}可用命令")
            print(
                '''
help ------ 查看可用命令
exit ------ 退出
time ------ 显示系统时间
sysinfo --- 显示设备信息
diag ------ 运行系统诊断
randompa -- 生成随机密码
surprise -- 超级大惊喜
ai -------- 打开ai对话
proxy ----- 设置或查看HTTP代理 (用法: proxy / proxy <地址> / proxy clear / proxy help(查看帮助))
RC4 ------- RC4加解密
smaiclub -- 打开SMAICLUB官网
setapikey - 设置AI模型的API密钥
setpassword 设置或更改您的软件密钥并添加密码找回功能
                '''
            )

        elif cmd1 == "setpassword":
            global user_password, security_questions
            print(f"{h2}开始设置新的软件密钥...")

            # 1. 验证当前密码
            current_pass_to_check = user_password if user_password else "114514"
            verify_pass = input(f"{h1}请输入当前密钥以进行验证: ")

            if verify_pass != current_pass_to_check:
                print(f"{h1}{Fore.RED}当前密钥验证失败，操作已取消。{Style.RESET_ALL}")
                continue  # 返回主命令循环

            # 2. 设置新密码
            while True:
                new_password = input(f"{h1}请输入您的新密钥: ")
                confirm_password = input(f"{h1}请再次输入以确认: ")
                if new_password == confirm_password:
                    if new_password:
                        break
                    else:
                        print(f"{h1}{Fore.RED}密钥不能为空，请重新输入。{Style.RESET_ALL}")
                else:
                    print(f"{h1}{Fore.RED}两次输入的密钥不匹配，请重新输入。{Style.RESET_ALL}")

            # 3. 设置自定义密保问题
            print(f"\n{h2}接下来，请设置三个您自己的密保问题和答案。")
            new_questions = {}
            for i in range(3):
                while True:
                    question = input(f"{h3}请输入第 {i + 1} 个自定义问题: ")
                    if question:
                        break
                    else:
                        print(f"{h3}{Fore.RED}问题不能为空，请重新输入。{Style.RESET_ALL}")

                while True:
                    answer = input(f"{h3}请输入该问题的答案: ")
                    if answer:
                        break
                    else:
                        print(f"{h3}{Fore.RED}答案不能为空，请重新输入。{Style.RESET_ALL}")
                new_questions[question] = answer

            # 4. 保存凭证
            FALCON_jd.save_credentials(new_password, new_questions)
            # 更新全局变量以便当前会话也能感知变化
            user_password = new_password
            security_questions = new_questions
            print(f"\n{h2}{Fore.GREEN}新密钥和密保问题已设置成功并加密保存！{Style.RESET_ALL}")
            print(f"{h2}设置将在下次启动程序时生效。")


        elif cmd1 == "exit":
            print("正在退出...")
            time.sleep(0.5)
            print("系统已关闭")
            os._exit(0)

        elif cmd1 == "diag":
            FALCON_jd.jdt2("正在检查核心运行状态 ", 0.5)
            FALCON_jd.jdt2("正在检查系统运行状态 ", 0.1)
            print("核心状态正常")
            print("系统运行正常")

        elif cmd1 == "setapikey":
            global deepseek_api_key, gemini_api_key
            print(f"{h2}开始设置API密钥...")
            new_deepseek_key = input(f"{h3}请输入DeepSeek API密钥: ")
            new_gemini_key = input(f"{h3}请输入Gemini API密钥: ")
            FALCON_jd.save_api_keys(new_deepseek_key, new_gemini_key)
            deepseek_api_key = new_deepseek_key
            gemini_api_key = new_gemini_key
            print(f"{h2}API密钥已加密并保存。")

        elif cmd1 == "ai":
            # 新增：在进入选择前，检查是否至少有一个API密钥存在
            if not deepseek_api_key and not gemini_api_key:
                print(f"{h2}{Fore.YELLOW}警告: 尚未设置任何API密钥。请先使用 'setapikey' 命令进行设置。{Style.RESET_ALL}")
                continue  # 跳过后续代码，直接返回主命令行

            print(f"{h3}请选择一个AI模型:")
            print("1. DeepSeek")
            print("2. Gemini(需使用科学上网并使用Proxy命令设置代理链接)")
            print("3. 返回主菜单")  # 新增：退出选项
            choice = ""

            # 循环直到用户输入有效选项（1, 2, 或 3）
            while choice not in ["1", "2", "3"]:
                choice = input(f"{h3}请输入选择 (1/2/3): ")

            # 新增：如果用户选择3，则直接返回主命令行
            if choice == "3":
                continue

            # --- 如果选择DeepSeek ---
            elif choice == "1":
                print(f"{h3}正在启动DeepSeek对话...")
                FALCON_jd.jdt2("正在连接", 0.01)
                print("基于DeepSeek API")
                print("AI对话已启动, 输入 aiquit 退出")
                while True:
                    q1 = input(h5_deepseek)
                    if q1 == "aiquit":
                        break
                    else:
                        DCai.ai1(q1, deepseek_api_key)

            # --- 如果选择Gemini ---
            elif choice == "2":
                print(f"{h3}请选择一个Gemini模型:")
                print("1. gemini-2.5-pro (推荐, 最强全能模型)")
                print("2. gemini-flash-latest (最新、速度快)")
                print("3. gemini-flash-lite-latest (速度更快, 但能力较弱)")
                model_choice = ""
                models = {
                    "1": "gemini-2.5-pro",
                    "2": "gemini-flash-latest",
                    "3": "gemini-flash-lite-latest"
                }
                while model_choice not in models:
                    model_choice = input(f"{h3}请输入模型选择 (1/2/3): ")
                selected_model = models[model_choice]
                print(f"{h3}正在启动Gemini对话 (模型: {selected_model})...")
                FALCON_jd.jdt2("正在连接，如果加载速度过慢请打开全局模式或TUN模式", 0.01)
                print("基于Google Gemini API")
                print("AI对话已启动, 输入 aiquit 退出")
                h5_gemini = f"{Fore.GREEN}AI(Gemini)>>>>>> {Style.RESET_ALL}"
                while True:
                    q1 = input(h5_gemini)
                    if q1 == "aiquit":
                        break
                    else:
                        DCai_Gemini.ai_gemini_chat(q1, selected_model, gemini_api_key)

        elif cmd1.startswith("proxy"):
            global current_proxy
            cmd_parts = cmd1.split()
            if len(cmd_parts) == 1:
                print(f"{h2}当前代理: {current_proxy}")
            elif len(cmd_parts) == 2:
                action = cmd_parts[1]
                if action.lower() == "help":
                    print(
                        f'''
{h2}[代理设置帮助]
本程序需要通过HTTP代理才能连接到Gemini服务器。你需要从你的代理软件中找到HTTP代理端口号。

{Fore.YELLOW}在哪里查找代理地址和端口号？{Style.RESET_ALL}

  {Fore.CYAN}1. 对于 Clash for Windows / Clash Verge:{Style.RESET_ALL}
     - 前往 "Settings" (设置) 页面。
     - 在 "Port" (端口) 或 "Mixed Port" (混合端口) 部分，找到端口号。
     - 默认通常是 {Fore.GREEN}7890{Style.RESET_ALL}。
     - 所以，你需要输入的命令是: {Fore.GREEN}proxy http://127.0.0.1:7890{Style.RESET_ALL}

  {Fore.CYAN}2. 对于 v2rayN:{Style.RESET_ALL}
     - 前往 "设置" -> "参数设置"。
     - 在底部找到 "本地监听端口" 部分，查看 "Http代理" 的端口号。
     - 默认通常是 {Fore.GREEN}10809{Style.RESET_ALL}。
     - 所以，你需要输入的命令是: {Fore.GREEN}proxy http://127.0.0.1:10809{Style.RESET_ALL}

  {Fore.CYAN}3. 对于 Shadowsocks:{Style.RESET_ALL}
     - 右键点击任务栏图标，查看 "服务器" -> "编辑服务器"。
     - 里面通常会显示本地SOCKS5代理端口，但你需要的是HTTP代理。
     - 你可能需要在 "选项设置" 里启用HTTP代理，并查看其端口。
     - 默认HTTP端口通常是 {Fore.GREEN}10808{Style.RESET_ALL}。

{Fore.YELLOW}总结:{Style.RESET_ALL}
  - 地址通常都是你自己的电脑，即 {Fore.GREEN}127.0.0.1{Style.RESET_ALL}。
  - 你需要找到你软件对应的 {Fore.GREEN}HTTP端口号{Style.RESET_ALL}。
  - 使用命令 {Fore.GREEN}proxy http://127.0.0.1:[你的端口号]{Style.RESET_ALL} 来设置。
'''
                    )
                elif action.lower() == "clear":
                    os.environ.pop('HTTP_PROXY', None)
                    os.environ.pop('HTTPS_PROXY', None)
                    current_proxy = "无"
                    print(f"{h2}代理已清除。")
                else:
                    proxy_address = action
                    if not proxy_address.startswith("http://") and not proxy_address.startswith("https://"):
                        print(f"{h3}错误：代理地址格式不正确，应以 'http://' 或 'https://' 开头。")
                    else:
                        os.environ['HTTP_PROXY'] = proxy_address
                        os.environ['HTTPS_PROXY'] = proxy_address
                        current_proxy = proxy_address
                        print(f"{h2}代理已成功设置为: {proxy_address}")
                        print(f"{h2}现在可以尝试使用 'ai' 命令连接Gemini了。")
            else:
                print(f'{h3}"{cmd1}" 属于无效命令。正确用法: proxy / proxy <地址> / proxy clear / proxy help')

        elif cmd1 == "time":
            local_time = time.localtime()
            formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            print(h4, formatted_time)

        elif cmd1 == "sysinfo":
            time.sleep(0.5)
            print("[设备信息]")
            time.sleep(0.1)
            print("核心: 量子神经网络 v2.86")
            time.sleep(0.1)
            print("处理器: 光子计算阵列 v5.69")
            time.sleep(0.1)
            print("内存: 42PB 频率9877654232MHz")
            time.sleep(0.1)
            print("存储: 1.685672YB 量子晶体存储")
            time.sleep(0.1)
            print("网络: 全球量子加密骨干网 (1872节点)")
            time.sleep(0.1)
            print("安全级别: 114514级")

        elif cmd1 == "randompa":
            time.sleep(1)
            FALCON_jd.random16(100)
            print("随机密码已生成")

        elif cmd1 == "surprise":
            print("请不要佩戴耳机")
            print("请不要佩戴耳机")
            print("请不要佩戴耳机")
            time.sleep(1)
            print("3")
            time.sleep(1)
            print("2")
            time.sleep(1)
            print("1")
            time.sleep(1)
            FALCON_jd.f2()
            FALCON_jd.f1()

        elif cmd1 == "RC4":
            print(f"{h3}RC4 加解密工具。")
            choice = ""
            while choice not in ["1", "2"]:
                choice = input(f"{h3}请选择操作: (1) 加密 (2) 解密: ")
            if choice == "1":
                data_to_encrypt = input(f"{h3}请输入需要加密的明文: ")
                encryption_key = input(f"{h3}请输入加密密钥: ")
                encrypted_result = FALCON_jd.rc4_encrypt_command(data_to_encrypt, encryption_key)
                print(f"{h2}加密完成。")
                print(f"{h2}密文: {encrypted_result}")
            elif choice == "2":
                data_to_decrypt = input(f"{h3}请输入需要解密的密文: ")
                decryption_key = input(f"{h3}请输入解密密钥: ")
                decrypted_result = FALCON_jd.rc4_decrypt_command(data_to_decrypt, decryption_key)
                print(f"{h2}解密完成。")
                print(f"{h2}明文: {decrypted_result}")

        elif cmd1 == "smaiclub":
            FALCON_jd.open_club_website()
            print(f"{h2}已打开官网。")

        else:
            print(f'{h3}"{cmd1}" 属于无效命令')
            continue


# --- 程序主入口 ---
load_all_data()
start1()
start2()
command1()