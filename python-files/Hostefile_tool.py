import csv
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import ipaddress


def read_csv(file_path):
    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = [row for row in reader if any(field.strip() for field in row)]
            if not rows:
                messagebox.showerror("Error", "Die Datei ist leer oder enthält nur Leerzeilen.")
                return [], []
            header, *data = rows
            return header, data
    except FileNotFoundError:
        messagebox.showerror("Error", f"Datei nicht gefunden: {file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Fehler beim Lesen: {e}")
    return [], []


def format_config(data, ip_idx, host_idx):
    known = {}
    for row in data:
        if len(row) <= max(ip_idx, host_idx):
            continue
        ip = row[ip_idx].strip().strip("'\"")
        host = row[host_idx].strip().strip("'\"").replace(' ', '_')
        if ip and host:
            known.setdefault(ip, [])
            if host not in known[ip]:
                known[ip].append(host)
    return known


def test_for_ipv4_or_ipv6(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def clean_sigtran_hosts(hosts):
    sig = [h for h in hosts if 'SIGTRAN' in h.upper()]
    if len(sig) == len(hosts):
        return [sig[-1]]
    return [h for h in hosts if h not in sig]


def add_extra_rules(known):
    for ip, hosts in list(known.items()):
        if not test_for_ipv4_or_ipv6(ip):
            known.pop(ip)
            continue
        if len(hosts) > 1:
            known[ip] = clean_sigtran_hosts(hosts)
    return known


class ManualCollisionResolver:
    def __init__(self, parent, collisions):
        self.parent = parent
        self.collisions = list(collisions.items())
        self.total = len(self.collisions)
        self.index = 0
        self.resolved = {}
        self.cancelled = False

        self.dlg = tk.Toplevel(parent)
        self.dlg.title("Manuelle Kollisionsauflösung")
        self.dlg.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.dlg.grab_set()
        self.dlg.columnconfigure(0, weight=1)

        self.prog_lbl = ttk.Label(self.dlg, text="Fortschritt: 0 von 0")
        self.prog_lbl.grid(row=0, column=0, sticky='w', padx=10, pady=(10,0))
        self.prog = ttk.Progressbar(self.dlg, maximum=self.total, length=300, mode='determinate')
        self.prog.grid(row=1, column=0, sticky='we', padx=10, pady=5)

        self.lbl = ttk.Label(self.dlg, text="")
        self.lbl.grid(row=2, column=0, sticky='w', padx=10, pady=(5,0))
        self.var = tk.StringVar()
        self.radio_frame = ttk.Frame(self.dlg)
        self.radio_frame.grid(row=3, column=0, sticky='w', padx=10, pady=5)

        btns = ttk.Frame(self.dlg)
        btns.grid(row=4, column=0, sticky='e', padx=10, pady=10)
        ttk.Button(btns, text="Weiter", command=self.on_next).grid(row=0, column=0, padx=5)
        ttk.Button(btns, text="Abbrechen", command=self.on_cancel).grid(row=0, column=1, padx=5)
        self.dlg.bind("<Key>", self.on_key)
        self.show()
        self.dlg.wait_window()

    def show(self):
        ip, hosts = self.collisions[self.index]
        self.lbl.config(text=f"IP {ip}: Wähle einen Host")
        self.prog_lbl.config(text=f"Fortschritt: {self.index+1} von {self.total}")
        self.prog['value'] = self.index
        for w in self.radio_frame.winfo_children():
            w.destroy()
        self.var.set(hosts[0])
        for i,h in enumerate(hosts[:5]):
            ttk.Radiobutton(self.radio_frame, text=f"{i+1}. {h}", variable=self.var, value=h).grid(row=i, column=0, sticky='w')

    def on_key(self, e):
        if e.char in '12345':
            idx = int(e.char)-1
            ip, hosts = self.collisions[self.index]
            if idx < len(hosts):
                self.var.set(hosts[idx])
                self.on_next()

    def on_next(self):
        ip,_ = self.collisions[self.index]
        self.resolved[ip] = self.var.get()
        self.index += 1
        if self.index < self.total:
            self.show()
        else:
            self.prog['value'] = self.total
            self.dlg.destroy()

    def on_cancel(self):
        if messagebox.askyesno("Abbrechen?", "Auflösung wirklich abbrechen? "):
            self.cancelled = True
            self.dlg.destroy()


def write_hosts(entries, add_ip, path, append=False):
    mode = 'a' if append else 'w'
    with open(path, mode, encoding='utf-8') as f:
        for ip,host in sorted(entries.items()):
            line = f"{ip} {host}_({ip})\n" if add_ip else f"{ip} {host}\n"
            f.write(line)


def main():
    root = tk.Tk()
    ttk.Style().theme_use('xpnative')
    root.title("Hosts Generator")
    root.geometry("600x420")

    nb = ttk.Notebook(root)
    nb.pack(fill='both', expand=True)

    # === Tab1: Neue Hosts Datei ===
    tab1 = ttk.Frame(nb)
    nb.add(tab1, text="Create Hosts")

    csv1 = tk.StringVar(); ip1=ttk.Combobox(tab1,state='readonly'); host1=ttk.Combobox(tab1,state='readonly'); add1=tk.BooleanVar()
    mode_csv1 = tk.StringVar(value='manual')

    def browse1():
        p = filedialog.askopenfilename(filetypes=[("CSV","*.csv"),("All","*")])
        if p: csv1.set(p); load1()
    def load1():
        h,d = read_csv(csv1.get());
        if h: ip1['values']=h; host1['values']=h; ip1.current(0); host1.current(0); tab1.data,tab1.h=h,d

    ttk.Label(tab1,text="CSV File:").grid(row=0,column=0,padx=10,pady=10,sticky='e')
    ttk.Entry(tab1,textvariable=csv1).grid(row=0,column=1,sticky='ew',padx=5,pady=10)
    ttk.Button(tab1,text="Browse",command=browse1).grid(row=0,column=2,padx=10,pady=10)
    ttk.Label(tab1,text="IP Column:").grid(row=1,column=0,padx=10,sticky='e')
    ip1.grid(row=1,column=1,sticky='w',padx=5)
    ttk.Checkbutton(tab1,text="Include IP",variable=add1).grid(row=1,column=2)
    ttk.Label(tab1,text="Host Column:").grid(row=2,column=0,padx=10,sticky='e')
    host1.grid(row=2,column=1,sticky='w',padx=5)

    cf1=ttk.LabelFrame(tab1,text="CSV Collision", padding=(10, 5))
    cf1.grid(row=3,column=0,columnspan=3,sticky='ew',padx=10)
    for i,(t,v) in enumerate([("Manual","manual"),("First","auto_first"),("Last","auto_last")]):
        ttk.Radiobutton(cf1,text=t,variable=mode_csv1,value=v).grid(row=0,column=i,padx=10)

    def run1():
        if not hasattr(tab1,'data'): return messagebox.showerror("Error","CSV laden!")
        hdr,dat = tab1.h,tab1.data
        cfg = add_extra_rules(format_config(dat,hdr.index(ip1.get()),hdr.index(host1.get())))
        # CSV internal collision
        if mode_csv1.get()!='manual':
            res={ip:(hosts[0] if mode_csv1.get()=='auto_first' else hosts[-1]) for ip,hosts in cfg.items()}
        else:
            coll={ip:hosts for ip,hosts in cfg.items() if len(hosts)>1}
            res={ip:hosts[0] for ip,hosts in cfg.items() if len(hosts)==1}
            if coll:
                mr=ManualCollisionResolver(root,coll)
                if mr.cancelled: return
                res.update(mr.resolved)
        dst=filedialog.asksaveasfilename(initialfile="hosts.txt")
        if dst: write_hosts(res,add1.get(),dst,append=False); messagebox.showinfo("Done","Erstellt.")

    btn1=ttk.Frame(tab1, padding=(10, 5))
    btn1.grid(row=4,column=0,columnspan=3,sticky='e')
    ttk.Button(btn1,text="Create Hosts",command=run1).grid(row=0,column=0,padx=5)
    ttk.Button(btn1,text="Exit",command=root.destroy).grid(row=0,column=1)

    # === Tab2: Append Hosts ===
    tab2 = ttk.Frame(nb)
    nb.add(tab2, text="Append Hosts")

    csv2=tk.StringVar(); ip2=ttk.Combobox(tab2,state='readonly'); host2=ttk.Combobox(tab2,state='readonly'); add2=tk.BooleanVar()
    hosts_file=tk.StringVar()
    mode_csv2=tk.StringVar(value='manual')
    mode_exist=tk.StringVar(value='keep_old')

    def browse_csv2():
        p=filedialog.askopenfilename(filetypes=[("CSV","*.csv"),("All","*")])
        if p: csv2.set(p); load2()
    def load2():
        h,d=read_csv(csv2.get())
        if h: ip2['values']=h; host2['values']=h; ip2.current(0); host2.current(0); tab2.data,tab2.h=h,d
    def browse_hosts():
        p=filedialog.askopenfilename(filetypes=[("Text","*.txt"),("All","*")])
        if p: hosts_file.set(p)
    #padding=(10, 5)
    # Widgets
    ttk.Label(tab2,text="CSV File:").grid(row=0,column=0,padx=10,pady=5,sticky='e')
    ttk.Entry(tab2,textvariable=csv2).grid(row=0,column=1,sticky='ew',padx=5)
    ttk.Button(tab2,text="Browse",command=browse_csv2).grid(row=0,column=2)
    ttk.Label(tab2,text="Hosts File:").grid(row=1,column=0,padx=10,pady=5,sticky='e')
    ttk.Entry(tab2,textvariable=hosts_file).grid(row=1,column=1,sticky='ew',padx=5)
    ttk.Button(tab2,text="Browse",command=browse_hosts).grid(row=1,column=2)
    ttk.Label(tab2,text="IP Column:").grid(row=2,column=0,padx=10,sticky='e')
    ip2.grid(row=2,column=1,sticky='w',padx=5)
    ttk.Checkbutton(tab2,text="Include IP",variable=add2).grid(row=2,column=2)
    ttk.Label(tab2,text="Host Column:").grid(row=3,column=0,padx=10,sticky='e')
    host2.grid(row=3,column=1,sticky='w',padx=5)

    # CSV internal collisions
    cf2=ttk.LabelFrame(tab2,text="CSV Collision",padding=(10, 5))
    cf2.grid(row=4,column=0,columnspan=3,sticky='ew',padx=10)
    for i,(t,v) in enumerate([("Manual","manual"),("First","auto_first"),("Last","auto_last")]):
        ttk.Radiobutton(cf2,text=t,variable=mode_csv2,value=v).grid(row=0,column=i,padx=10)
    # Existing file collisions
    cf3=ttk.LabelFrame(tab2,text="Hosts-File Collision",padding=(10, 5))
    cf3.grid(row=5,column=0,columnspan=3,sticky='ew',padx=10)
    for i,(t,v) in enumerate([("Keep Old","keep_old"),("Use New","keep_new"),("Manual","manual")]):
        ttk.Radiobutton(cf3,text=t,variable=mode_exist,value=v).grid(row=0,column=i,padx=10)

    def run2():
        if not hasattr(tab2,'data'): return messagebox.showerror("Error","CSV laden!")
        h,d=tab2.h,tab2.data
        path=hosts_file.get()
        if not path or not os.path.exists(path): return messagebox.showerror("Error","Hosts-Datei wählen!")
        # load existing
        existing={}
        with open(path,'r',encoding='utf-8') as f:
            for l in f:
                p=l.strip().split();
                if len(p)>=2: existing[p[0]] = p[1]
        # CSV config
        cfg=add_extra_rules(format_config(d,h.index(ip2.get()),h.index(host2.get())))
        # apply CSV collision
        if mode_csv2.get()!='manual':
            temp={ip:(hosts[0] if mode_csv2.get()=='auto_first' else hosts[-1]) for ip,hosts in cfg.items()}
        else:
            coll={ip:hosts for ip,hosts in cfg.items() if len(hosts)>1}
            temp={ip:hosts[0] for ip,hosts in cfg.items() if len(hosts)==1}
            if coll:
                mr=ManualCollisionResolver(root,coll)
                if mr.cancelled: return
                temp.update(mr.resolved)
        # detect existing collisions
        exist_coll={ip:[existing[ip],temp[ip]] for ip in temp if ip in existing}
        out={}
        # handle exist collisions
        if mode_exist.get()=='keep_old':
            out={ip:temp[ip] for ip in temp if ip not in exist_coll}
        elif mode_exist.get()=='keep_new':
            # rewrite without old collisions
            with open(path,'r',encoding='utf-8') as f:lines=f.readlines()
            with open(path,'w',encoding='utf-8') as f:
                for l in lines:
                    ip=l.strip().split()[0] if l.strip() else ''
                    if ip not in exist_coll: f.write(l)
            out=temp
        else:
            if exist_coll:
                mr=ManualCollisionResolver(root,exist_coll)
                if mr.cancelled: return
                out.update(mr.resolved)
            out.update({ip:temp[ip] for ip in temp if ip not in exist_coll})
        write_hosts(out,add2.get(),path,append=True)
        messagebox.showinfo("Done","Daten angehängt.")

    btn2=ttk.Frame(tab2, padding=(10, 5))
    btn2.grid(row=6,column=0,columnspan=3,sticky='e')
    ttk.Button(btn2,text="Append Hosts",command=run2).grid(row=0,column=0,padx=5)
    ttk.Button(btn2,text="Exit",command=root.destroy).grid(row=0,column=1)

    root.mainloop()

if __name__ == '__main__':
    main()
