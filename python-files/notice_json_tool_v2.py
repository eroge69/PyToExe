import json
import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip
import os
import re
from datetime import datetime
from zoneinfo import ZoneInfo

HISTORY_FILE = 'notice_history.json'
STATE_OPTIONS = ['안내', '예정', '진행중', '보류', '확인중', '완료']
ARTICLE_TYPE_OPTIONS = ['공지', '이벤트', '점검', '노트']

class NoticeJSONTool:

    def __init__(self, root):
        self.root = root
        self.root.title('공지 JSON 변환기')
        self.notices = self.load_history()
        self.tabControl = ttk.Notebook(root)
        self.manual_tab = ttk.Frame(self.tabControl)
        self.sheet_tab = ttk.Frame(self.tabControl)
        self.history_tab = ttk.Frame(self.tabControl)
        self.tabControl.add(self.manual_tab, text='직접 입력')
        self.tabControl.add(self.sheet_tab, text='시트 복사 입력')
        self.tabControl.add(self.history_tab, text='히스토리')
        self.tabControl.pack(expand=1, fill='both')
        self.setup_manual_tab()
        self.setup_sheet_tab()
        self.setup_history_tab()

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def save_history(self):
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.notices, f, ensure_ascii=False, indent=4)

    def parse_time_str(self, time_str):
        if not time_str:
            return ''
        try:
            dt = datetime.strptime(time_str, '%Y-%m-%d %H:%M')
            dt = dt.replace(tzinfo=ZoneInfo('Asia/Seoul'))
            return dt.isoformat()
        except Exception:
            return None

    def parse_target_servers(self, ts_str):
        if not ts_str:
            return []
        try:
            return [int(x.strip()) for x in ts_str.split(',') if x.strip()]
        except ValueError:
            return None

    def setup_manual_tab(self):
        ttk.Label(self.manual_tab, text='제목:').pack()
        self.title_entry = tk.Entry(self.manual_tab, width=100)
        self.title_entry.pack()
        ttk.Label(self.manual_tab, text='내용:').pack()
        self.content_text = tk.Text(self.manual_tab, height=30, width=100)
        self.content_text.pack()
        self.state_var = tk.StringVar(value=STATE_OPTIONS[0])
        self.article_type_var = tk.StringVar(value=ARTICLE_TYPE_OPTIONS[0])
        ttk.Label(self.manual_tab, text='State:').pack()
        ttk.OptionMenu(self.manual_tab, self.state_var, STATE_OPTIONS[0], *STATE_OPTIONS).pack()
        ttk.Label(self.manual_tab, text='Article Type:').pack()
        ttk.OptionMenu(self.manual_tab, self.article_type_var, ARTICLE_TYPE_OPTIONS[0], *ARTICLE_TYPE_OPTIONS).pack()
        ttk.Label(self.manual_tab, text='Start Time (KST, YYYY-MM-DD HH:MM):').pack()
        self.start_time_entry = tk.Entry(self.manual_tab, width=100)
        self.start_time_entry.pack()
        ttk.Label(self.manual_tab, text='Disappear Time (KST, YYYY-MM-DD HH:MM):').pack()
        self.disappear_time_entry = tk.Entry(self.manual_tab, width=100)
        self.disappear_time_entry.pack()
        ttk.Label(self.manual_tab, text='End Time (KST, YYYY-MM-DD HH:MM):').pack()
        self.end_time_entry = tk.Entry(self.manual_tab, width=100)
        self.end_time_entry.pack()
        ttk.Label(self.manual_tab, text='Min Version:').pack()
        self.min_version_entry = tk.Entry(self.manual_tab, width=100)
        self.min_version_entry.pack()
        ttk.Label(self.manual_tab, text='Max Version:').pack()
        self.max_version_entry = tk.Entry(self.manual_tab, width=100)
        self.max_version_entry.pack()
        ttk.Label(self.manual_tab, text='Target Servers (comma-separated):').pack()
        self.target_servers_entry = tk.Entry(self.manual_tab, width=100)
        self.target_servers_entry.pack()
        ttk.Button(self.manual_tab, text='히스토리에 추가', command=self.add_manual_notice).pack()

    def setup_sheet_tab(self):
        ttk.Label(self.sheet_tab, text='제목은 탭으로 구분, 내용은 "내용" 형식으로 줄바꿈 및 탭으로 구분:').pack()
        self.sheet_text = tk.Text(self.sheet_tab, height=30, width=120)
        self.sheet_text.pack()
        self.sheet_state_var = tk.StringVar(value=STATE_OPTIONS[0])
        self.sheet_article_type_var = tk.StringVar(value=ARTICLE_TYPE_OPTIONS[0])
        ttk.Label(self.sheet_tab, text='State:').pack()
        ttk.OptionMenu(self.sheet_tab, self.sheet_state_var, STATE_OPTIONS[0], *STATE_OPTIONS).pack()
        ttk.Label(self.sheet_tab, text='Article Type:').pack()
        ttk.OptionMenu(self.sheet_tab, self.sheet_article_type_var, ARTICLE_TYPE_OPTIONS[0], *ARTICLE_TYPE_OPTIONS).pack()
        ttk.Label(self.sheet_tab, text='Start Time (KST, YYYY-MM-DD HH:MM):').pack()
        self.sheet_start_time_entry = tk.Entry(self.sheet_tab, width=100)
        self.sheet_start_time_entry.pack()
        ttk.Label(self.sheet_tab, text='Disappear Time (KST, YYYY-MM-DD HH:MM):').pack()
        self.sheet_disappear_time_entry = tk.Entry(self.sheet_tab, width=100)
        self.sheet_disappear_time_entry.pack()
        ttk.Label(self.sheet_tab, text='End Time (KST, YYYY-MM-DD HH:MM):').pack()
        self.sheet_end_time_entry = tk.Entry(self.sheet_tab, width=100)
        self.sheet_end_time_entry.pack()
        ttk.Label(self.sheet_tab, text='Min Version:').pack()
        self.sheet_min_version_entry = tk.Entry(self.sheet_tab, width=100)
        self.sheet_min_version_entry.pack()
        ttk.Label(self.sheet_tab, text='Max Version:').pack()
        self.sheet_max_version_entry = tk.Entry(self.sheet_tab, width=100)
        self.sheet_max_version_entry.pack()
        ttk.Label(self.sheet_tab, text='Target Servers (comma-separated):').pack()
        self.sheet_target_servers_entry = tk.Entry(self.sheet_tab, width=100)
        self.sheet_target_servers_entry.pack()
        ttk.Button(self.sheet_tab, text='히스토리에 추가', command=self.add_sheet_notices).pack()

    def setup_history_tab(self):
        left_frame = ttk.Frame(self.history_tab)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.history_listbox = tk.Listbox(left_frame, width=50, height=30, selectmode=tk.EXTENDED)
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.history_listbox.bind('<<ListboxSelect>>', self.show_preview)
        scrollbar = ttk.Scrollbar(left_frame, command=self.history_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_listbox.config(yscrollcommand=scrollbar.set)
        right_frame = ttk.Frame(self.history_tab)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.preview_text = tk.Text(right_frame, width=80, height=30)
        self.preview_text.pack()
        btn_frame = ttk.Frame(right_frame)
        btn_frame.pack()
        ttk.Button(btn_frame, text='복사', command=self.copy_selected_notice).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text='삭제', command=self.delete_selected_notices).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text='수정', command=self.modify_selected_notice).pack(side=tk.LEFT, padx=5)
        self.update_history_list()

    def update_history_list(self):
        self.history_listbox.delete(0, tk.END)
        for idx, notice in enumerate(self.notices):
            self.history_listbox.insert(tk.END, f"{idx + 1}. {notice['title']}")

    def show_preview(self, event):
        selection = self.history_listbox.curselection()
        if not selection:
            return
        idx = selection[0]
        notice = self.notices[idx]
        preview = f"제목: {notice['title']}\n\n내용:\n" + '\n'.join([c['content'] for c in notice['contents']])
        self.preview_text.delete('1.0', tk.END)
        self.preview_text.insert(tk.END, preview)

    def split_content(self, text):
        lines = text.splitlines()
        return [{'type': 0, 'content': line, 'whiteSpaceLine': 0} for line in lines]

    def generate_json(self, title, content, state, article_type,
                      start_time, disappear_time, end_time, min_version, max_version, target_servers):
        return {
            'title': title,
            'contents': self.split_content(content),
            'articleId': '',
            'thumbnail': '',
            'state': STATE_OPTIONS.index(state),
            'articleType': ARTICLE_TYPE_OPTIONS.index(article_type),
            'startTime': start_time,
            'disappearTime': disappear_time,
            'endTime': end_time,
            'minVersion': min_version,
            'maxVersion': max_version,
            'targetServers': target_servers
        }

    def add_manual_notice(self):
        title = self.title_entry.get().strip()
        content = self.content_text.get('1.0', tk.END).strip()
        state = self.state_var.get()
        article_type = self.article_type_var.get()
        st = self.parse_time_str(self.start_time_entry.get().strip())
        if st is None:
            messagebox.showerror('시간 형식 오류', 'Start Time 형식을 확인하세요.')
            return
        dis = self.parse_time_str(self.disappear_time_entry.get().strip())
        if dis is None:
            messagebox.showerror('시간 형식 오류', 'Disappear Time 형식을 확인하세요.')
            return
        et = self.parse_time_str(self.end_time_entry.get().strip())
        if et is None:
            messagebox.showerror('시간 형식 오류', 'End Time 형식을 확인하세요.')
            return
        minv = self.min_version_entry.get().strip()
        maxv = self.max_version_entry.get().strip()
        ts = self.parse_target_servers(self.target_servers_entry.get().strip())
        if ts is None:
            messagebox.showerror('서버 형식 오류', 'Target Servers 형식을 확인하세요.')
            return
        self.add_notice(title, content, state, article_type, st, dis, et, minv, maxv, ts)

    def add_sheet_notices(self):
        raw_data = self.sheet_text.get('1.0', tk.END).strip()
        lines = raw_data.splitlines()
        if not lines or len(lines) < 2:
            messagebox.showerror('형식 오류', '제목 줄과 내용 줄이 필요합니다.')
            return
        titles = [t.strip() for t in lines[0].split('\t') if t.strip()]
        content_text = '\n'.join(lines[1:])
        contents = re.findall('"(.*?)"', content_text, re.DOTALL)
        if len(titles) != 5 or len(contents) != 5:
            messagebox.showerror('형식 오류', f'제목 5개, 내용 5개가 필요합니다. 현재 제목 {len(titles)}개, 내용 {len(contents)}개')
            return
        state = self.sheet_state_var.get()
        article_type = self.sheet_article_type_var.get()
        st = self.parse_time_str(self.sheet_start_time_entry.get().strip())
        if st is None:
            messagebox.showerror('시간 형식 오류', 'Start Time 형식을 확인하세요.')
            return
        dis = self.parse_time_str(self.sheet_disappear_time_entry.get().strip())
        if dis is None:
            messagebox.showerror('시간 형식 오류', 'Disappear Time 형식을 확인하세요.')
            return
        et = self.parse_time_str(self.sheet_end_time_entry.get().strip())
        if et is None:
            messagebox.showerror('시간 형식 오류', 'End Time 형식을 확인하세요.')
            return
        minv = self.sheet_min_version_entry.get().strip()
        maxv = self.sheet_max_version_entry.get().strip()
        ts = self.parse_target_servers(self.sheet_target_servers_entry.get().strip())
        if ts is None:
            messagebox.showerror('서버 형식 오류', 'Target Servers 형식을 확인하세요.')
            return
        for title, content in zip(titles, contents):
            self.add_notice(title, content, state, article_type, st, dis, et, minv, maxv, ts)

    def add_notice(self, title, content, state, article_type, start_time, disappear_time, end_time, min_version, max_version, target_servers):
        json_data = self.generate_json(title, content, state, article_type, start_time, disappear_time, end_time, min_version, max_version, target_servers)
        self.notices.append(json_data)
        self.save_history()
        self.update_history_list()
        messagebox.showinfo('추가 완료', f"'{title}' 공지가 히스토리에 추가되었습니다.")

    def get_selected_index(self):
        selection = self.history_listbox.curselection()
        if selection:
            return selection

    def copy_selected_notice(self):
        selection = self.get_selected_index()
        if selection:
            if len(selection) == 1:
                idx = selection[0]
                pyperclip.copy(json.dumps(self.notices[idx], ensure_ascii=False, indent=4))
                messagebox.showinfo('복사 완료', 'JSON이 클립보드에 복사되었습니다.')
            else:
                combined = [self.notices[i] for i in selection]
                pyperclip.copy(json.dumps(combined, ensure_ascii=False, indent=4))
                messagebox.showinfo('복사 완료', '여러 공지의 JSON이 클립보드에 복사되었습니다.')

    def delete_selected_notices(self):
        selected_indices = list(self.history_listbox.curselection())
        if not selected_indices:
            return
        for idx in reversed(selected_indices):
            del self.notices[idx]
        self.save_history()
        self.update_history_list()
        self.preview_text.delete('1.0', tk.END)
        messagebox.showinfo('삭제 완료', '선택한 공지가 삭제되었습니다.')

    def modify_selected_notice(self):
        idx = self.get_selected_index()[0] if self.get_selected_index() else None
        if idx is not None:
            notice = self.notices[idx]
            modify_win = tk.Toplevel(self.root)
            modify_win.title('공지 수정')
            tk.Label(modify_win, text='제목:').pack()
            title_entry = tk.Entry(modify_win, width=80)
            title_entry.insert(0, notice['title'])
            title_entry.pack()
            tk.Label(modify_win, text='내용:').pack()
            content_text = tk.Text(modify_win, width=80, height=30)
            content_text.insert('1.0', '\n'.join([c['content'] for c in notice['contents']]))
            content_text.pack()
            state_var = tk.StringVar(value=STATE_OPTIONS[notice['state']])
            article_type_var = tk.StringVar(value=ARTICLE_TYPE_OPTIONS[notice['articleType']])
            tk.Label(modify_win, text='State:').pack()
            ttk.OptionMenu(modify_win, state_var, state_var.get(), *STATE_OPTIONS).pack()
            tk.Label(modify_win, text='Article Type:').pack()
            ttk.OptionMenu(modify_win, article_type_var, article_type_var.get(), *ARTICLE_TYPE_OPTIONS).pack()
            tk.Label(modify_win, text='Start Time (KST, YYYY-MM-DD HH:MM):').pack()
            start_entry = tk.Entry(modify_win, width=80)
            orig_start = notice.get('startTime', '')
            if orig_start:
                try:
                    dt = datetime.fromisoformat(orig_start).astimezone(ZoneInfo('Asia/Seoul'))
                    start_entry.insert(0, dt.strftime('%Y-%m-%d %H:%M'))
                except:
                    start_entry.insert(0, orig_start)
            start_entry.pack()
