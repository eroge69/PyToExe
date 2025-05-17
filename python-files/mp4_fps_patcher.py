import struct
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox

def patch_atom(atom_name, data, fps_in, fps_out=30):
    count = 0
    start = 0
    scale_ts = fps_out / fps_in
    atom_bytes = atom_name.encode('utf-8')

    while True:
        found = data.find(atom_bytes, start)
        if found < 0:
            break

        if atom_name == 'mvhd':
            timescale_offset = found + 12
            duration_offset = found + 16
        elif atom_name == 'mdhd':
            timescale_offset = found + 12
            duration_offset = found + 16
        else:
            break

        try:
            timescale = struct.unpack('>I', data[timescale_offset:timescale_offset+4])[0]
            duration = struct.unpack('>I', data[duration_offset:duration_offset+4])[0]
            new_duration = int(duration * scale_ts)
            data[duration_offset:duration_offset+4] = struct.pack('>I', new_duration)
            count += 1
        except Exception as e:
            print(f"Error patching {atom_name}: {e}")

        start = found + 4
    return count

def patch_mp4(in_file, out_file, fps_in):
    with open(in_file, 'rb') as f:
        data = bytearray(f.read())
    patch_atom('mvhd', data, fps_in)
    patch_atom('mdhd', data, fps_in)
    with open(out_file, 'wb') as f:
        f.write(data)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('MP4 → 30 FPS Patch')
        self.resizable(False, False)

        try:
            img = tk.PhotoImage(file='myicon.png')
            self.iconphoto(False, img)
        except Exception:
            pass

        self.update_idletasks()
        width, height = (400, 120)
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry(f'{width}x{height}+{x}+{y}')

        self.input_path = tk.StringVar()
        self.input_fps = tk.DoubleVar(value=60.0)

        tk.Label(self, text='Source MP4:').grid(row=0, column=0, padx=5, pady=5, sticky='e')
        tk.Entry(self, textvariable=self.input_path, width=40).grid(row=0, column=1)
        tk.Button(self, text='Browse…', command=self.browse).grid(row=0, column=2, padx=5)

        tk.Label(self, text='Original FPS:').grid(row=1, column=0, padx=5, pady=5, sticky='e')
        tk.Entry(self, textvariable=self.input_fps, width=8).grid(row=1, column=1, sticky='w')

        tk.Button(self, text='Patch to 30 FPS', command=self.run).grid(row=2, column=1, pady=10)

    def browse(self):
        p = filedialog.askopenfilename(title='Select MP4', filetypes=[('MP4 files', '*.mp4')])
        if p:
            self.input_path.set(p)

    def run(self):
        inp = self.input_path.get()
        if not inp:
            return messagebox.showerror('Error', 'Please select an MP4 file.')
        try:
            out = inp.replace('.mp4', '_patched.mp4')
            shutil.copy(inp, out)
            patch_mp4(out, out, self.input_fps.get())
            messagebox.showinfo('Success', f'Patched file saved as:\n{out}')
        except Exception as e:
            messagebox.showerror('Error', str(e))

if __name__ == '__main__':
    App().mainloop()
