import time
import sys

# 检查并安装库
def check_and_install_libraries():
    try:
        import ping3
    except ImportError:
        print("未找到 ping3 库。请手动安装：")
        print("运行命令: pip install ping3")
        return False  # 返回 False 表示未能加载 ping3 库

    try:
        from colorama import Fore, Style, init
        init(autoreset=True)
    except ImportError:
        print("未找到 colorama 库。请手动安装：")
        print("运行命令: pip install colorama")
        return False  # 返回 False 表示未能加载 colorama 库
    
    return True  # 如果所有库都已安装，返回 True

# 提示用户关于脚本的说明
def show_intro():
    intro_text = """
    =============================================
    📌 Python 自动 Ping 工具
    =============================================

    ✅ 程序会 ping 指定的 IP 地址或域名，指定次数，并显示每次 ping 的结果
    ✅ 用户需要手动输入目标 IP 地址/域名、ping 的次数和每次 ping 的间隔时间
    ✅ 脚本会根据 ping 的结果显示绿色（成功）或红色（失败）
    ✅ 支持 ping 域名和 IP 地址

    🔹 请根据提示输入相关信息，按回车继续...
    """
    print(intro_text)

# 执行 ping 操作
def ping_ip(ip_address, count, interval):
    success_count = 0
    failure_count = 0

    print(f"正在 Ping {ip_address} 具有 32 字节的数据:")

    try:
        for ping_number in range(1, count + 1):
            response_time = ping3.ping(ip_address, timeout=2)

            print(f"正在进行第{ping_number}次 ping，结果：", end="")

            if response_time is None:
                print(Fore.RED + "请求超时。")
                failure_count += 1
            else:
                print(Fore.GREEN + f"回复来自 {ip_address}: 字节=32 时间={response_time:.2f}ms TTL=64")
                success_count += 1

            time.sleep(interval)  # 等待指定的间隔时间后再进行下一次 ping

    except KeyboardInterrupt:
        print("\nPing 操作被用户终止。")

    print(f"\nPing 统计信息:")
    print(f"    数据包: 已发送 = {success_count + failure_count}，已接收 = {success_count}，丢失 = {failure_count} ({failure_count / (success_count + failure_count) * 100:.2f}% 丢失)，")

# 主程序
if __name__ == "__main__":
    if not check_and_install_libraries():  # 如果没有安装所需库，显示提示并退出
        print("脚本需要的库未安装，请手动安装缺失的库，然后重新运行脚本。")
        sys.exit(1)  # 退出脚本

    show_intro()  # 显示介绍，按回车继续

    # 获取用户输入
    ip_to_ping = input("请输入要 ping 的 IP 地址或域名: ")
    ping_count = input("请输入 ping 的次数: ")
    ping_interval = input("请输入 ping 的间隔时间（秒）: ")

    # 验证用户输入是否为有效数字
    try:
        ping_count = int(ping_count)
        ping_interval = int(ping_interval)

        if ping_count <= 0 or ping_interval <= 0:
            print("次数和间隔时间必须是正整数，请重新输入。")
            sys.exit(1)

    except ValueError:
        print("请输入有效的数字！")
        sys.exit(1)

    # 执行 ping 操作
    ping_ip(ip_to_ping, ping_count, ping_interval)
