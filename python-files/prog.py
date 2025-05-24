import tkinter as tk
from tkinter import messagebox
import random
import os
from PIL import Image, ImageTk

class GIFPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GIF播放器")
        self.root.attributes('-topmost', True)  # 窗口置顶
        self.root.overrideredirect(True)  # 隐藏窗口边框和标题栏
        
        # 初始GIF文件
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.original_gif = os.path.join(self.base_dir, "image.gif")
        self.current_gif = self.original_gif
        
        # 窗口大小变化标志
        self.resize_flag = False
        
        # 拖动窗口相关变量
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0
        
        # 缩放比例
        self.scale_factor = 0.3
        
        # 检查初始GIF文件是否存在
        if not os.path.exists(self.original_gif):
            messagebox.showerror("错误", f"找不到初始GIF文件: {self.original_gif}")
            root.destroy()
            return
        
        # 加载GIF
        self.gif_frames = []
        self.current_frame = 0
        self.frame_delay = 0
        self.original_frames = []  # 存储原始帧，用于调整大小
        self.load_gif(self.current_gif)
        
        # 创建Canvas用于显示GIF
        self.canvas = tk.Canvas(root, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.image_item = self.canvas.create_image(0, 0, anchor=tk.NW)
        
        # 绑定点击事件和鼠标事件
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drag)
        
        # 显示第一帧
        self.show_frame()
        
        # 自动播放GIF
        self.play_gif()
    
    def load_gif(self, gif_path):
        """加载GIF文件并提取所有帧"""
        try:
            gif = Image.open(gif_path)
            
            # 存储原始GIF尺寸
            self.original_width, self.original_height = gif.width, gif.height
            
            # 计算缩放后的尺寸
            scaled_width = int(self.original_width * self.scale_factor)
            scaled_height = int(self.original_height * self.scale_factor)
            
            # 设置窗口大小为缩放后的尺寸
            if not self.resize_flag:
                self.root.geometry(f"{scaled_width}x{scaled_height}")
            
            self.gif_frames = []
            self.original_frames = []
            self.current_frame = 0
            
            try:
                while True:
                    frame = gif.copy()
                    self.original_frames.append(frame.copy())
                    
                    # 缩放帧
                    if self.resize_flag:
                        # 使用当前窗口大小
                        window_width = self.root.winfo_width()
                        window_height = self.root.winfo_height()
                        resized_frame = frame.resize((window_width, window_height), Image.LANCZOS)
                    else:
                        # 使用缩放比例
                        resized_frame = frame.resize((scaled_width, scaled_height), Image.LANCZOS)
                    
                    photo = ImageTk.PhotoImage(resized_frame)
                    self.gif_frames.append((photo, gif.info['duration']))
                    gif.seek(len(self.gif_frames))  # 移动到下一帧
            except EOFError:
                pass  # 所有帧已加载完
            
            if self.gif_frames:
                self.frame_delay = self.gif_frames[0][1]
            else:
                messagebox.showerror("错误", f"无法加载GIF文件: {gif_path}")
                self.root.destroy()
                
        except Exception as e:
            messagebox.showerror("错误", f"加载GIF时出错: {str(e)}")
            self.root.destroy()
    
    def resize_frames(self, width, height):
        """调整所有帧的大小"""
        self.gif_frames = []
        
        for frame in self.original_frames:
            resized_frame = frame.resize((width, height), Image.LANCZOS)
            photo = ImageTk.PhotoImage(resized_frame)
            self.gif_frames.append((photo, self.frame_delay))
    
    def show_frame(self):
        """显示当前帧"""
        if 0 <= self.current_frame < len(self.gif_frames):
            frame, _ = self.gif_frames[self.current_frame]
            self.canvas.itemconfig(self.image_item, image=frame)
            self.canvas.image = frame
    
    def play_gif(self):
        """播放GIF动画"""
        if len(self.gif_frames) > 1:
            self.current_frame = (self.current_frame + 1) % len(self.gif_frames)
            self.show_frame()
            self.play_id = self.root.after(self.frame_delay, self.play_gif)
    
    def on_click(self, event):
        """处理点击事件"""
        # 生成1-5的随机数
        randomnum = random.randint(1, 5)
        print(f"生成随机数: {randomnum}")
        
        # 构建随机GIF文件名
        randomimg = os.path.join(self.base_dir, f"{randomnum}.gif")
        
        # 检查随机GIF文件是否存在
        if os.path.exists(randomimg):
            # 停止当前GIF播放
            if hasattr(self, "play_id"):
                self.root.after_cancel(self.play_id)
            
            # 加载并显示随机GIF
            self.current_gif = randomimg
            self.resize_flag = True  # 标记为已调整过大小
            self.load_gif(self.current_gif)
            
            # 获取当前窗口大小
            window_width = self.root.winfo_width()
            window_height = self.root.winfo_height()
            
            # 如果窗口有实际大小，调整GIF大小
            if window_width > 10 and window_height > 10:
                self.resize_frames(window_width, window_height)
            
            self.show_frame()
            
            # 5000毫秒后恢复原始GIF
            self.root.after(3000, self.restore_original_gif)
        else:
            messagebox.showwarning("警告", f"找不到随机GIF文件: {randomimg}")
    
    def restore_original_gif(self):
        """恢复原始GIF播放"""
        if self.current_gif != self.original_gif:
            # 停止当前GIF播放
            if hasattr(self, "play_id"):
                self.root.after_cancel(self.play_id)
            
            # 加载并显示原始GIF
            self.current_gif = self.original_gif
            self.load_gif(self.current_gif)
            
            # 获取当前窗口大小
            window_width = self.root.winfo_width()
            window_height = self.root.winfo_height()
            
            # 如果窗口有实际大小，调整GIF大小
            if window_width > 10 and window_height > 10:
                self.resize_frames(window_width, window_height)
            
            self.show_frame()
            self.play_gif()
    
    def start_drag(self, event):
        """开始拖动窗口"""
        self.dragging = True
        self.offset_x = event.x
        self.offset_y = event.y
    
    def on_drag(self, event):
        """拖动窗口过程"""
        if self.dragging:
            x = self.root.winfo_pointerx() - self.offset_x
            y = self.root.winfo_pointery() - self.offset_y
            self.root.geometry(f"+{x}+{y}")
    
    def stop_drag(self, event):
        """停止拖动窗口"""
        self.dragging = False

if __name__ == "__main__":
    root = tk.Tk()
    app = GIFPlayerApp(root)
    
    # 添加右键菜单退出功能
    def quit_app(event):
        root.destroy()
    
    root.bind("<Button-3>", quit_app)
    
    root.mainloop()    
