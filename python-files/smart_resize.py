
import os
import sys
import io
from PIL import Image
from rembg import remove

# 网络共享目标路径
SAVE_PATHS = {
    (300, 240): r"\\Egboffice\egb\Image",
    (100, 80): r"\\Egboffice\egb\Icon"
}

# 缩放+白边填充，不裁切
def resize_with_padding(image, target_size):
    target_w, target_h = target_size
    image_w, image_h = image.size
    scale = min(target_w / image_w, target_h / image_h)
    new_w = int(image_w * scale)
    new_h = int(image_h * scale)
    resized = image.resize((new_w, new_h), Image.LANCZOS)
    
    # 创建白底新图
    final = Image.new('RGB', (target_w, target_h), (255, 255, 255))
    paste_x = (target_w - new_w) // 2
    paste_y = (target_h - new_h) // 2
    final.paste(resized, (paste_x, paste_y), resized)
    return final

# 单张图处理流程
def process_image(image_path):
    try:
        with open(image_path, 'rb') as f:
            input_data = f.read()
        output_data = remove(input_data, alpha_matting=False)
        image_rgba = Image.open(io.BytesIO(output_data)).convert("RGBA")
        base_name = os.path.splitext(os.path.basename(image_path))[0]

        for size, folder in SAVE_PATHS.items():
            os.makedirs(folder, exist_ok=True)
            output_img = resize_with_padding(image_rgba, size)
            save_path = os.path.join(folder, base_name + ".jpg")
            output_img.save(save_path)
            print(f"✅ 已保存：{save_path}")

    except Exception as e:
        print(f"❌ 处理失败：{image_path} 错误：{e}")

# 程序入口
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("请将图片文件拖到此程序上运行。")
    else:
        for path in sys.argv[1:]:
            print(f"📷 正在处理：{path}")
            process_image(path)
