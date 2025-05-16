import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
from queue import Queue

class SpaceSniffer:
    def __init__(self, root):
        self.root = root
        self.root.title("SpaceSniffer - 磁盘空间分析工具")
        self.root.geometry("1000x600")
        
        self.queue = Queue()
        self.size_cache = {}  # 缓存目录大小（路径: 大小）
        self.loading = set()  # 记录正在加载的节点
        
        self.create_widgets()
        self.create_right_click_menu()  # 初始化右键菜单

    def create_widgets(self):
        # 目录选择框架
        dir_frame = ttk.Frame(self.root, padding=10)
        dir_frame.pack(fill=tk.X)

        self.dir_entry = ttk.Entry(dir_frame, width=80)
        self.dir_entry.pack(side=tk.LEFT, padx=5)

        ttk.Button(dir_frame, text="选择目录", command=self.choose_directory).pack(side=tk.LEFT, padx=5)
        self.scan_btn = ttk.Button(dir_frame, text="开始扫描", command=self.start_scan)
        self.scan_btn.pack(side=tk.LEFT, padx=5)

        # 层级树状图
        tree_frame = ttk.Frame(self.root, padding=10)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=('size',),
            show='tree headings',
            selectmode='browse',
            displaycolumns='size'
        )
        self.tree.heading('#0', text='文件夹路径')
        self.tree.heading('size', text='占用空间', command=lambda: self.sort_tree('size', False))
        self.tree.column('size', width=150, anchor='e')
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 绑定双击展开和右键事件
        self.tree.bind('<Double-1>', self.on_double_click)
        self.tree.bind('<Button-3>', self.on_right_click)  # 右键点击事件

        # 滚动条
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.status_label = ttk.Label(self.root, text="就绪", padding=10)
        self.status_label.pack(fill=tk.X)

    def create_right_click_menu(self):
        """创建右键菜单"""
        self.right_click_menu = tk.Menu(self.root, tearoff=0)
        self.right_click_menu.add_command(
            label="打开文件夹",
            command=self.open_selected_directory
        )

    def on_right_click(self, event):
        """右键点击时显示菜单"""
        # 获取点击的节点
        item = self.tree.identify_row(event.y)
        if item:
            # 选中当前点击的节点
            self.tree.selection_set(item)
            # 在鼠标位置显示菜单
            self.right_click_menu.post(event.x_root, event.y_root)

    def open_selected_directory(self):
        """打开选中的目录"""
        selected_items = self.tree.selection()
        if not selected_items:
            return

        dir_path = self.tree.item(selected_items[0], 'text')  # 获取选中节点的路径
        if not os.path.isdir(dir_path):
            messagebox.showerror("错误", "路径无效或非目录")
            return

        try:
            os.startfile(dir_path)  # Windows专用打开目录方法
        except Exception as e:
            messagebox.showerror("打开失败", f"无法打开目录：{str(e)}")

    def choose_directory(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, dir_path)

    def start_scan(self):
        target_dir = self.dir_entry.get()
        if not os.path.isdir(target_dir):
            messagebox.showerror("错误", "请选择有效的文件夹路径")
            return

        self.clear_tree()
        self.scan_btn.config(state=tk.DISABLED)
        self.status_label.config(text="初始化根目录...")

        # 添加根目录节点（初始大小0）
        root_node = self.tree.insert(
            '', tk.END,
            text=target_dir,
            values=(self.format_size(0),),
            open=False
        )
        self.tree.item(root_node, tags=('root',))
        
        # 启动根目录大小计算线程
        threading.Thread(
            target=self.calculate_dir_size,
            args=(target_dir, root_node),
            daemon=True
        ).start()

    def calculate_dir_size(self, dir_path, node):
        """计算目录大小（递归子目录）"""
        total_size = 0
        try:
            for root, dirs, files in os.walk(dir_path):
                # 计算当前目录文件大小
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        total_size += os.path.getsize(file_path)
                    except (OSError, PermissionError):
                        continue
        except PermissionError:
            total_size = -1  # 标记无权限
        
        self.size_cache[dir_path] = total_size
        self.queue.put(('update_size', node, total_size))

        # 根目录计算完成后启用按钮
        if self.tree.item(node, 'tags') == ('root',):
            self.queue.put(('scan_complete',))

    def on_double_click(self, event):
        """双击展开/加载子目录"""
        item = self.tree.identify_row(event.y)
        if not item or item in self.loading:
            return

        dir_path = self.tree.item(item, 'text')
        if self.tree.item(item, 'open'):
            self.tree.item(item, open=False)
        else:
            if not self.tree.get_children(item):
                self.loading.add(item)
                self.status_label.config(text=f"加载 {dir_path} 的子目录...")
                threading.Thread(
                    target=self.load_subdirectories,
                    args=(item, dir_path),
                    daemon=True
                ).start()
            self.tree.item(item, open=True)

    def load_subdirectories(self, parent_node, parent_path):
        """加载父目录的直接子目录"""
        subdirs = []
        try:
            for entry in os.scandir(parent_path):
                if entry.is_dir(follow_symlinks=False):
                    subdirs.append(entry.path)
        except PermissionError:
            self.queue.put(('show_error', parent_node, "无权限访问该目录"))
            return
        finally:
            self.loading.discard(parent_node)

        # 创建子目录节点并计算大小
        for subdir in subdirs:
            sub_node = self.tree.insert(
                parent_node, tk.END,
                text=subdir,
                values=(self.format_size(0),),
                open=False
            )
            threading.Thread(
                target=self.calculate_dir_size,
                args=(subdir, sub_node),
                daemon=True
            ).start()

        self.queue.put(('update_status', f"加载完成：{parent_path}"))

    def process_queue(self):
        """处理队列中的界面更新"""
        while not self.queue.empty():
            item = self.queue.get()
            if item[0] == 'update_size':
                _, node, size = item
                self.tree.item(node, values=(self.format_size(size),))
            elif item[0] == 'scan_complete':
                self.scan_btn.config(state=tk.NORMAL)
                self.status_label.config(text="扫描完成，双击目录查看子目录")
            elif item[0] == 'show_error':
                _, node, msg = item
                self.tree.item(node, text=f"{self.tree.item(node, 'text')} (错误)")
                messagebox.showerror("错误", msg)
            elif item[0] == 'update_status':
                _, msg = item
                self.status_label.config(text=msg)
        
        self.root.after(100, self.process_queue)

    def clear_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.size_cache.clear()
        self.loading.clear()

    @staticmethod
    def format_size(bytes_size):
        if bytes_size == -1:
            return "无权限"
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        while bytes_size >= 1024 and unit_index < len(units)-1:
            bytes_size /= 1024
            unit_index += 1
        return f"{bytes_size:.2f} {units[unit_index]}" if bytes_size != -1 else "无权限"

    def sort_tree(self, column, reverse):
        """按大小排序当前层级目录"""
        parent = self.tree.selection() or self.tree.get_children('')[0]
        children = self.tree.get_children(parent)
        
        items = [(self.tree.set(child, column), child) for child in children]
        def sort_key(item):
            value, _ = item
            if value == "无权限":
                return -float('inf')
            num, unit = value.split()
            units = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3, 'TB': 1024**4}
            return float(num) * units[unit]

        items.sort(key=sort_key, reverse=reverse)
        for index, (value, child) in enumerate(items):
            self.tree.move(child, parent, index)
        
        arrow = '▲' if reverse else '▼'
        self.tree.heading(column, text=f"占用空间 {arrow}", 
                         command=lambda: self.sort_tree(column, not reverse))

if __name__ == "__main__":
    root = tk.Tk()
    app = SpaceSniffer(root)
    root.after(100, app.process_queue)  # 启动队列处理
    root.mainloop()
