import os
import sys

def remove_empty_folders(path):
    """核心功能：递归删除空文件夹"""
    deleted = set()
    
    # 自底向上遍历目录树
    for root, dirs, files in os.walk(path, topdown=False):
        current_dir = os.path.normpath(root)
        
        # 检测是否为空目录
        if not os.listdir(current_dir):
            try:
                os.rmdir(current_dir)
                deleted.add(current_dir)
                print(f"🗑️ 已删除：{current_dir}")
            except OSError as e:
                print(f"❌ 删除失败（{e.strerror}）：{current_dir}")

def get_script_directory():
    """获取脚本所在目录的绝对路径"""
    script_path = os.path.abspath(sys.argv[0])
    return os.path.dirname(script_path)

def is_root_directory(path):
    """安全防护：禁止操作系统根目录"""
    path = os.path.normpath(path)
    if os.name == 'nt':  # Windows系统
        if os.path.splitdrive(path)[1] in ('\\', '/'):
            return True
    else:  # Linux/macOS
        if path == '/':
            return True
    return False

def safety_remove_empty_folders(target_dir):
    """安全执行入口"""
    target_dir = os.path.normpath(target_dir)
    
    if not os.path.exists(target_dir):
        print(f"❌ 错误：目标目录不存在 - {target_dir}")
        return
    
    if is_root_directory(target_dir):
        print(f"⛔ 危险！拒绝操作系统根目录 - {target_dir}")
        return

    print(f"📍 待清理路径：{os.path.abspath(target_dir)}")
    if input("⚠️ 确认开始删除空文件夹？(输入 YES 并回车): ") != "YES":
        print("🛑 操作已取消")
        return

    remove_empty_folders(target_dir)
    print("✅ 操作完成，请手动验证结果")

if __name__ == "__main__":
    # 强制路径锁定
    script_dir = get_script_directory()
    current_dir = os.getcwd()

    # 路径安全检测
    print(f"🔍 脚本位置：{script_dir}")
    print(f"📂 当前工作目录：{current_dir}")
    
    if script_dir != current_dir:
        print("⚠️ 警告：工作目录与脚本位置不一致！")
        if input("是否切换到脚本目录？(y/n): ").lower() == 'y':
            os.chdir(script_dir)
            print(f"🔄 已切换到：{script_dir}")
            current_dir = script_dir
        else:
            print("⏹️ 终止执行以确保安全")
            sys.exit(1)

    safety_remove_empty_folders(current_dir)
