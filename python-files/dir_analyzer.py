"""
📂 智能目录分析工具（修正版）
"""

import os
from pathlib import Path

def smart_analyzer(max_depth=3, exclude_dirs=[".git", "node_modules"]):
    base_dir = Path(__file__).parent.absolute()
    output_file = base_dir / "精简统计报告.txt"
    
    print(f"🔍 扫描根目录：{base_dir} (最大深度：{max_depth})")
    
    stats = {"总目录": 0, "总文件": 0}
    tree = [f"{base_dir.name}/"]

    def scan(path, current_depth=1, prefix=""):
        if current_depth > max_depth:
            return
        
        try:
            with os.scandir(path) as entries:
                dirs, files = [], []
                for entry in entries:
                    if entry.is_dir():
                        if entry.name not in exclude_dirs:
                            dirs.append(entry)
                    else:
                        stats["总文件"] += 1

                print(f"⚙️ 正在扫描：{Path(path).relative_to(base_dir)}".ljust(50), end='\r')
                
                for idx, d in enumerate(sorted(dirs, key=lambda x: x.name.lower())):
                    is_last = idx == len(dirs)-1
                    pointer = "└── " if is_last else "├── "
                    tree_line = f"{prefix}{pointer}{d.name}/"
                    tree.append(tree_line)
                    
                    stats["总目录"] += 1
                    next_prefix = "    " if is_last else "│   "
                    scan(d.path, current_depth+1, prefix + next_prefix)
                    
        except PermissionError:
            pass

    scan(base_dir)
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(tree)+"\n\n")
        f.write(f"📊 统计结果：\n目录数量：{stats['总目录']}\n文件数量：{stats['总文件']}")
    
    print(f"\n✅ 生成完成！文件位置：{output_file}")

if __name__ == "__main__":
    # ⚠️ 注意参数名已修正
    smart_analyzer(
        max_depth=3,
        exclude_dirs=[".git", ".idea", "venv"]
    )
