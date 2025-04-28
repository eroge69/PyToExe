import os
import zipfile
import math
import joblib
import pefile
import pandas as pd
import numpy as np
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import scrypt
from Crypto.Random import get_random_bytes
import tkinter as tk
from tkinter import Frame, Label, Button, filedialog, messagebox, simpledialog
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.feature_selection import SelectFromModel
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix

# ─── GLOBAL STORE FOR MALWARE PAGE ─────────────────────────────────
clf_global = None
features_global = None

# ─── UTILITIES FOR MALWARE PAGE ───────────────────────────────────
def get_entropy(data: bytes) -> float:
    if not data: return 0.0
    freq = [0]*256
    for b in data: freq[b] += 1
    ent = 0.0
    l = len(data)
    for f in freq:
        if f:
            p = f / l
            ent -= p * math.log2(p)
    return ent

def extract_infos(path: str) -> dict:
    pe = pefile.PE(path, fast_load=True)
    pe.parse_data_directories(directories=[
        pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
        pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"],
        pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_RESOURCE"],
        pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_LOAD_CONFIG"],
    ])
    oh = pe.OPTIONAL_HEADER; fh = pe.FILE_HEADER

    info = {
        "Machine": fh.Machine,
        "SizeOfOptionalHeader": fh.SizeOfOptionalHeader,
        "Characteristics": fh.Characteristics,
        "MajorLinkerVersion": oh.MajorLinkerVersion,
        "MinorLinkerVersion": oh.MinorLinkerVersion,
        "SizeOfCode": oh.SizeOfCode,
        "SizeOfInitializedData": oh.SizeOfInitializedData,
        "SizeOfUninitializedData": oh.SizeOfUninitializedData,
        "AddressOfEntryPoint": oh.AddressOfEntryPoint,
        "BaseOfCode": getattr(oh, "BaseOfCode", 0),
        "BaseOfData": getattr(oh, "BaseOfData", 0),
        "ImageBase": oh.ImageBase,
        "SectionAlignment": oh.SectionAlignment,
        "FileAlignment": oh.FileAlignment,
        "MajorOperatingSystemVersion": oh.MajorOperatingSystemVersion,
        "MinorOperatingSystemVersion": oh.MinorOperatingSystemVersion,
        "MajorImageVersion": oh.MajorImageVersion,
        "MinorImageVersion": oh.MinorImageVersion,
        "MajorSubsystemVersion": oh.MajorSubsystemVersion,
        "MinorSubsystemVersion": oh.MinorSubsystemVersion,
        "SizeOfImage": oh.SizeOfImage,
        "SizeOfHeaders": oh.SizeOfHeaders,
        "CheckSum": oh.CheckSum,
        "Subsystem": oh.Subsystem,
        "DllCharacteristics": oh.DllCharacteristics,
        "SizeOfStackReserve": oh.SizeOfStackReserve,
        "SizeOfStackCommit": oh.SizeOfStackCommit,
        "SizeOfHeapReserve": oh.SizeOfHeapReserve,
        "SizeOfHeapCommit": oh.SizeOfHeapCommit,
        "LoaderFlags": oh.LoaderFlags,
        "NumberOfRvaAndSizes": oh.NumberOfRvaAndSizes,
    }

    # sections
    ents, raws, virs = [], [], []
    for s in pe.sections:
        data = s.get_data()
        ents.append(get_entropy(data))
        raws.append(s.SizeOfRawData)
        virs.append(s.Misc_VirtualSize)
    n = len(ents)
    if n:
        info.update({
            "SectionsNb": n,
            "SectionsMeanEntropy": np.mean(ents),
            "SectionsMinEntropy": np.min(ents),
            "SectionsMaxEntropy": np.max(ents),
            "SectionsMeanRawsize": np.mean(raws),
            "SectionsMinRawsize": np.min(raws),
            "SectionsMaxRawsize": np.max(raws),
            "SectionsMeanVirtualsize": np.mean(virs),
            "SectionsMinVirtualsize": np.min(virs),
            "SectionsMaxVirtualsize": np.max(virs),
        })
    else:
        for k in ["SectionsNb","SectionsMeanEntropy","SectionsMinEntropy","SectionsMaxEntropy",
                  "SectionsMeanRawsize","SectionsMinRawsize","SectionsMaxRawsize",
                  "SectionsMeanVirtualsize","SectionsMinVirtualsize","SectionsMaxVirtualsize"]:
            info[k] = 0

    # imports
    imps = getattr(pe, "DIRECTORY_ENTRY_IMPORT", [])
    dlls = len(imps)
    funcs = sum(len(x.imports) for x in imps)
    ords = sum(1 for x in imps for imp in x.imports if imp.name is None)
    info.update({
        "ImportsNbDLL": dlls,
        "ImportsNb": funcs,
        "ImportsNbOrdinal": ords
    })

    # exports
    e = getattr(pe, "DIRECTORY_ENTRY_EXPORT", None)
    info["ExportNb"] = len(e.symbols) if e else 0

    # resources
    r_ent, r_sz = [], []
    res = getattr(pe, "DIRECTORY_ENTRY_RESOURCE", None)
    if res:
        for entry in res.entries:
            if hasattr(entry, "directory"):
                for e in entry.directory.entries:
                    if hasattr(e, "data"):
                        size = e.data.struct.Size
                        data = pe.get_data(e.data.struct.OffsetToData, size)
                        r_ent.append(get_entropy(data))
                        r_sz.append(size)
    if r_ent:
        info.update({
            "ResourcesNb": len(r_ent),
            "ResourcesMeanEntropy": np.mean(r_ent),
            "ResourcesMinEntropy": np.min(r_ent),
            "ResourcesMaxEntropy": np.max(r_ent),
            "ResourcesMeanSize": np.mean(r_sz),
            "ResourcesMinSize": np.min(r_sz),
            "ResourcesMaxSize": np.max(r_sz),
        })
    else:
        for k in ["ResourcesNb","ResourcesMeanEntropy","ResourcesMinEntropy","ResourcesMaxEntropy",
                  "ResourcesMeanSize","ResourcesMinSize","ResourcesMaxSize"]:
            info[k] = 0

    # load config
    ld = oh.DATA_DIRECTORY[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_LOAD_CONFIG"]]
    info["LoadConfigurationSize"] = getattr(ld, "Size", 0)
    info["VersionInformationSize"] = 0

    return info

def train_and_save():
    global clf_global, features_global
    path = filedialog.askopenfilename(
        title="Select dataset CSV",
        filetypes=[("CSV","*.csv"),("All","*.*")]
    )
    if not path: return

    # sniff sep & read
    first = open(path, 'r', encoding='utf-8', errors='ignore').readline()
    sep = '|' if '|' in first else ','
    df = pd.read_csv(path, sep=sep, engine='python', on_bad_lines='skip')

    if 'Name' not in df.columns or 'legitimate' not in df.columns:
        return messagebox.showerror("Error","Dataset must have 'Name' and 'legitimate' columns.")

    df['Name'] = df['Name'].str.lower()
    df = df.set_index('Name', drop=False)
    y = df['legitimate'].astype(int)
    X = df.drop(columns=['Name','md5','legitimate'], errors='ignore')\
          .apply(pd.to_numeric, errors='coerce').fillna(0)

    # feature selection
    et = ExtraTreesClassifier(n_estimators=100, random_state=0)
    et.fit(X, y)
    sel = SelectFromModel(et, prefit=True, threshold='median')
    X_sel = sel.transform(X)
    features = X.columns[sel.get_support()].tolist()

    # train/test & RandomForest
    Xtr, Xte, ytr, yte = train_test_split(X_sel, y, test_size=0.2, stratify=y, random_state=42)
    clf = RandomForestClassifier(max_depth=2, random_state=0)
    clf.fit(Xtr, ytr)

    # quick report
    def rpt(name, Xx, yy):
        p = clf.predict(Xx)
        tn, fp, fn, tp = confusion_matrix(yy,p).ravel()
        messagebox.showinfo(
            name,
            f"Acc: {accuracy_score(yy,p):.2%}\n"
            f"F1:  {f1_score(yy,p):.2%}\n"
            f"FP rate: {fp/(fp+tn):.2%}\n"
            f"FN rate: {fn/(fn+tp):.2%}"
        )
    rpt(" TRAIN results", Xtr, ytr)
    rpt("  TEST results", Xte, yte)

    cls_path = filedialog.asksaveasfilename(
        title="Save classifier (.pkl)",
        defaultextension=".pkl",
        filetypes=[("Pickle","*.pkl")]
    )
    if not cls_path: return
    feat_path = os.path.splitext(cls_path)[0] + "_features.pkl"
    joblib.dump(clf, cls_path)
    joblib.dump(features, feat_path)

    clf_global = clf
    features_global = features
    messagebox.showinfo("Saved",
        f"Classifier → {cls_path}\nFeatures   → {feat_path}"
    )

def load_model():
    global clf_global, features_global
    # 1) classifier
    cls_p = filedialog.askopenfilename(
        title="Select trained classifier (.pkl)",
        filetypes=[("Pickle classifier","*.pkl")])
    if not cls_p: return
    # 2) features
    feat_p = filedialog.askopenfilename(
        title="Select feature-list (.pkl)",
        filetypes=[("Pickle features","*.pkl")])
    if not feat_p: return

    try:
        clf = joblib.load(cls_p)
        feats = joblib.load(feat_p)
    except Exception as e:
        return messagebox.showerror("Load error", str(e))

    if not hasattr(clf, "predict_proba") or not isinstance(feats, (list,tuple)):
        return messagebox.showerror("Invalid files","Wrong classifier or features file.")

    clf_global = clf
    features_global = feats
    messagebox.showinfo("Loaded",
        f"Classifier: {os.path.basename(cls_p)}\nFeatures: {os.path.basename(feat_p)}"
    )

def upload_and_predict():
    if clf_global is None or features_global is None:
        return messagebox.showwarning("No Model","Train or Load a model first.")
    exe = filedialog.askopenfilename(
        title="Select .exe to scan",
        filetypes=[("Executable","*.exe")])
    if not exe: return
    try:
        infos = extract_infos(exe)
    except Exception as e:
        return messagebox.showerror("PE parse failed", str(e))
    X = np.array([[infos.get(f,0) for f in features_global]])
    probs = clf_global.predict_proba(X)[0]
    mal_i = list(clf_global.classes_).index(0)
    malp = probs[mal_i]*100
    messagebox.showinfo("Result",
        f"{os.path.basename(exe)}\nMalware Probability: {malp:.2f}%"
    )

# ─── UTILITIES FOR ENCRYPTION PAGE ────────────────────────────
def encrypt_folder(folder_path, password):
    zip_path = folder_path + '.zip'
    enc_path = folder_path + '.encrypted.zip'
    if os.path.exists(enc_path):
        return messagebox.showwarning(
            "Blocked",
            "Already encrypted. Delete the existing `.encrypted.zip` first."
        )
    with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
        for r,ds,fs in os.walk(folder_path):
            for f in fs:
                full = os.path.join(r,f)
                z.write(full, os.path.relpath(full, folder_path))

    salt = get_random_bytes(16)
    key  = scrypt(password.encode(), salt, 32, N=2**14, r=8, p=1)
    cipher = AES.new(key, AES.MODE_GCM)
    data = open(zip_path,'rb').read()
    ct, tag = cipher.encrypt_and_digest(data)

    with open(enc_path,'wb') as outf:
        outf.write(salt)
        outf.write(cipher.nonce)
        outf.write(tag)
        outf.write(ct)

    os.remove(zip_path)
    messagebox.showinfo("Encrypted","Folder encrypted successfully!")

def decrypt_folder(enc_path):
    while True:
        pwd = simpledialog.askstring("Password","Enter password:", show='*')
        if pwd is None:
            if messagebox.askyesno("Back","Cancel decryption? Return to menu?"):
                return
            continue
        try:
            raw = open(enc_path,'rb').read()
            salt, nonce, tag, ct = raw[:16], raw[16:32], raw[32:48], raw[48:]
            key = scrypt(pwd.encode(), salt, 32, N=2**14, r=8, p=1)
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            pt = cipher.decrypt_and_verify(ct, tag)
            zpath = enc_path.replace('.encrypted.zip','.zip')
            open(zpath,'wb').write(pt)
            outdir = enc_path.replace('.encrypted.zip','_decrypted')
            with zipfile.ZipFile(zpath,'r') as z:
                z.extractall(outdir)
            os.remove(zpath)
            return messagebox.showinfo("Decrypted",f"Extracted to:\n{outdir}")
        except:
            if not messagebox.askretrycancel("Error","Wrong password or corrupted. Retry?"):
                return

# ─── APPLICATION PAGES ────────────────────────────────────────
class HomePage(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        Label(self, text="Malcrypt", font=("Arial",18)).pack(pady=20)
        Button(self, text="Malware Detection",
               width=24, command=lambda:controller.show_frame(MalwarePage)).pack(pady=8)
        Button(self, text="Secure Folder Encryption",
               width=24, command=lambda:controller.show_frame(EncryptPage)).pack(pady=8)
        Button(self, text="Exit", width=24, command=controller.destroy).pack(pady=8)

class MalwarePage(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        Label(self, text="Malware Detection", font=("Arial",16)).pack(pady=10)
        Button(self, text="Train & Save Model",   width=24, command=train_and_save).pack(pady=5)
        Button(self, text="Load Model",           width=24, command=load_model).pack(pady=5)
        Button(self, text="Scan .exe file",       width=24, command=upload_and_predict).pack(pady=5)
        Button(self, text="Back to Home",         width=24,
               command=lambda:controller.show_frame(HomePage)).pack(pady=5)
        Button(self, text="Exit", width=24, command=controller.destroy).pack(pady=5)

class EncryptPage(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        Label(self, text="Secure Folder Encryption", font=("Arial",16)).pack(pady=10)
        Button(self, text="Encrypt Folder", width=24, command=self.do_encrypt).pack(pady=5)
        Button(self, text="Decrypt Folder", width=24, command=self.do_decrypt).pack(pady=5)
        Button(self, text="Back to Home", width=24,
               command=lambda:controller.show_frame(HomePage)).pack(pady=5)
        Button(self, text="Exit", width=24, command=controller.destroy).pack(pady=5)

    def do_encrypt(self):
        pwd = None
        while not pwd:
            pwd = simpledialog.askstring("Set Password","Enter encryption password:", show='*')
            if pwd is None: return
            if not pwd: messagebox.showwarning("Warn","Password cannot be empty.")
        fld = filedialog.askdirectory(title="Select folder to encrypt")
        if fld: encrypt_folder(fld, pwd)

    def do_decrypt(self):
        f = filedialog.askopenfilename(
            title="Select .encrypted.zip",
            filetypes=[("Encrypted ZIP","*.encrypted.zip")])
        if f: decrypt_folder(f)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Malcrypt")
        self.geometry("360x300")
        self.resizable(False, False)
        self.update_idletasks()
        w,h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth()-w)//2
        y = (self.winfo_screenheight()-h)//2
        self.geometry(f"{w}x{h}+{x}+{y}")

        container = Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (HomePage, MalwarePage, EncryptPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(HomePage)

    def show_frame(self, cls):
        self.frames[cls].tkraise()

if __name__ == "__main__":
    App().mainloop()

