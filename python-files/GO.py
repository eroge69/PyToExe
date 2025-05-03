import os
import time

def format_timestamp(timestamp):
    """格式化時間戳為 YYYYMMDD-HHMMSS"""
    struct_time = time.localtime(timestamp)
    return time.strftime("%Y%m%d-%H%M%S", struct_time)

def batch_rename_png():
    """
    批量重命名當前目錄下所有 .png 文件，依照其建立日期格式化命名，並避免重複同步。
    """
    current_dir = os.getcwd()
    files = [f for f in os.listdir(current_dir) if f.lower().endswith(".png")]
    
    for filename in files:
        old_path = os.path.join(current_dir, filename)
        create_time = os.path.getctime(old_path)
        formatted_time = format_timestamp(create_time)
        new_name = f"PIC-{formatted_time}.PNG"
        
        # 如果文件名已經符合規則，則跳過
        if filename == new_name:
            continue
        
        new_path = os.path.join(current_dir, new_name)
        os.rename(old_path, new_path)
        print(f"Renamed: {filename} -> {new_name}")

if __name__ == "__main__":
    batch_rename_png()
