try:
    import pandas as pd
except ImportError:
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "缺少模組",
        "找不到 pandas 模組。\n\n請打開命令提示字元並執行：\n\npip install pandas -i https://pypi.tuna.tsinghua.edu.cn/simple"
    )
    raise

from tkinter import Tk, filedialog, messagebox
from openpyxl import load_workbook

def process_excel(file_path):
    xlsx = pd.ExcelFile(file_path)
    df1 = xlsx.parse('工作表1')
    data = df1.iloc[1:, 2].dropna().astype(str)
    names = data.str.extract(r'-(.+)$')[0].str.strip()
    summary = names.value_counts().reset_index()
    summary.columns = ['姓名', '次數']
    total = summary['次數'].sum()
    summary.loc[len(summary)] = ['總計', total]

    output_path = file_path.replace('.xlsx', '_處理結果.xlsx')
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        summary.to_excel(writer, sheet_name='工作表2', startrow=2, startcol=1, index=False)
        ws = writer.sheets['工作表2']
        ws['B2'] = '姓名'
        ws['C2'] = '次數'
    return output_path

def main():
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="請選擇含有工作表1的 Excel 檔案", filetypes=[("Excel files", "*.xlsx")])
    if not file_path:
        return

    try:
        output_file = process_excel(file_path)
        messagebox.showinfo("完成", f"處理完成！結果已儲存為：\n{output_file}")
    except Exception as e:
        messagebox.showerror("錯誤", f"發生錯誤：{str(e)}")

if __name__ == '__main__':
    main()
