# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ||                       WINDOWS GDI MAYHEM & FREAKOUT                     ||
# ||-------------------------------------------------------------------------||
# || This script is a playground for Windows GDI graphical effects,          ||
# || bytebeat audio generation, and a "freaky" system finale.                ||
# ||                                                                         ||
# || ### --- EXTREME CAUTION --- ###                                         ||
# || This script is designed to be disruptive and will attempt to REBOOT     ||
# || your computer.                                                          ||
# || - ONLY RUN IN A VIRTUAL MACHINE you don't mind resetting.               ||
# || - SAVE ALL WORK on your host system first.                              ||
# || - REQUIRES ADMINISTRATOR PRIVILEGES (it will try to get them).          ||
# || - The audio can be LOUD and ABRASIVE. Protect your ears!                ||
# ||                                                                         ||
# || You have been thoroughly warned! I am not responsible for anything.     ||
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import ctypes
import ctypes.wintypes as wintypes
import time
import random
import sys
import threading
import math
import struct # For packing WAV data for our bytebeat sounds

# --- Core Windows API Constants ---
SM_CXSCREEN, SM_CYSCREEN = 0, 1
SRCCOPY, NOTSRCCOPY, PATCOPY, PATINVERT, SRCINVERT, DSTINVERT, BLACKNESS, WHITENESS = \
    0x00CC0020, 0x00330008, 0x00F00021, 0x005A0049, 0x00660046, 0x00550009, 0x00000042, 0x00FF0062
OPTION_SHUTDOWN_SYSTEM = 6
CUSTOM_BSOD_CODE = 0xA7EBADF00D
TOKEN_ADJUST_PRIVILEGES, TOKEN_QUERY, SE_PRIVILEGE_ENABLED = 0x0020, 0x0008, 0x00000002
SE_SHUTDOWN_NAME = "SeShutdownPrivilege"
SND_MEMORY, SND_ASYNC, SND_LOOP, SND_PURGE = 0x0004, 0x0001, 0x0008, 0x0040
TRANSPARENT = 1
EWX_REBOOT, EWX_FORCEIFHUNG = 0x00000002, 0x00000010
SHTDN_REASON_MAJOR_OPERATINGSYSTEM, SHTDN_REASON_MINOR_RECONFIG, SHTDN_REASON_FLAG_PLANNED = \
    0x00020000, 0x00000004, 0x80000000
WS_POPUP, WS_VISIBLE = 0x80000000, 0x10000000
HWND_TOPMOST = wintypes.HWND(-1)
SWP_NOSIZE, SWP_NOMOVE, SWP_NOACTIVATE = 0x0001, 0x0002, 0x0010
WM_DESTROY, WM_PAINT, WM_KEYDOWN, VK_ESCAPE = 0x0002, 0x000F, 0x0100, 0x1B
CS_HREDRAW, CS_VREDRAW, IDC_ARROW, COLOR_WINDOW = 0x0002, 0x0001, 32512, 5
STRETCH_ANDSCANS, STRETCH_ORSCANS, STRETCH_DELETESCANS, STRETCH_HALFTONE = 1, 2, 3, 4

class LUID(ctypes.Structure): _fields_ = [("LowPart", wintypes.DWORD), ("HighPart", wintypes.LONG)]
class LUID_AND_ATTRIBUTES(ctypes.Structure): _fields_ = [("Luid", LUID), ("Attributes", wintypes.DWORD)]
class TOKEN_PRIVILEGES(ctypes.Structure): _fields_ = [("PrivilegeCount", wintypes.DWORD), ("Privileges", LUID_AND_ATTRIBUTES * 1)]
WNDPROCTYPE = ctypes.WINFUNCTYPE(wintypes.LPARAM, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
try: HCURSOR = wintypes.HCURSOR
except AttributeError: HCURSOR = wintypes.HANDLE
try: HICON = wintypes.HICON
except AttributeError: HICON = wintypes.HANDLE
class WNDCLASSEXW(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.UINT), ("style", wintypes.UINT), ("lpfnWndProc", WNDPROCTYPE),
                ("cbClsExtra", ctypes.c_int), ("cbWndExtra", ctypes.c_int), ("hInstance", wintypes.HINSTANCE),
                ("hIcon", HICON), ("hCursor", HCURSOR), ("hbrBackground", wintypes.HBRUSH),
                ("lpszMenuName", wintypes.LPCWSTR), ("lpszClassName", wintypes.LPCWSTR), ("hIconSm", HICON)]
class PAINTSTRUCT(ctypes.Structure):
    _fields_ = [("hdc", wintypes.HDC), ("fErase", wintypes.BOOL), ("rcPaint", wintypes.RECT),
                ("fRestore", wintypes.BOOL), ("fIncUpdate", wintypes.BOOL), ("rgbReserved", wintypes.BYTE * 32)]
class MSG(ctypes.Structure):
    _fields_ = [("hwnd", wintypes.HWND), ("message", wintypes.UINT), ("wParam", wintypes.WPARAM),
                ("lParam", wintypes.LPARAM), ("time", wintypes.DWORD), ("pt", wintypes.POINT)]

user32=ctypes.WinDLL('user32',use_last_error=True);gdi32=ctypes.WinDLL('gdi32',use_last_error=True)
ntdll=ctypes.WinDLL('ntdll',use_last_error=True);advapi32=ctypes.WinDLL('advapi32',use_last_error=True)
kernel32=ctypes.WinDLL('kernel32',use_last_error=True);winmm=ctypes.WinDLL('winmm',use_last_error=True)
shell32=ctypes.WinDLL('shell32',use_last_error=True)

GetDC=user32.GetDC;GetDC.argtypes=[wintypes.HWND];GetDC.restype=wintypes.HDC
ReleaseDC=user32.ReleaseDC;ReleaseDC.argtypes=[wintypes.HWND,wintypes.HDC];ReleaseDC.restype=ctypes.c_int
GetSystemMetrics=user32.GetSystemMetrics;GetSystemMetrics.argtypes=[ctypes.c_int];GetSystemMetrics.restype=ctypes.c_int
CreateSolidBrush=gdi32.CreateSolidBrush;CreateSolidBrush.argtypes=[wintypes.COLORREF];CreateSolidBrush.restype=wintypes.HBRUSH
SelectObject=gdi32.SelectObject;SelectObject.argtypes=[wintypes.HDC,wintypes.HGDIOBJ];SelectObject.restype=wintypes.HGDIOBJ
DeleteObject=gdi32.DeleteObject;DeleteObject.argtypes=[wintypes.HGDIOBJ];DeleteObject.restype=wintypes.BOOL
Rectangle=gdi32.Rectangle;Rectangle.argtypes=[wintypes.HDC,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int];Rectangle.restype=wintypes.BOOL
Ellipse=gdi32.Ellipse;Ellipse.argtypes=[wintypes.HDC,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int];Ellipse.restype=wintypes.BOOL
BitBlt=gdi32.BitBlt;BitBlt.argtypes=[wintypes.HDC,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,wintypes.HDC,ctypes.c_int,ctypes.c_int,wintypes.DWORD];BitBlt.restype=wintypes.BOOL
TextOutW=gdi32.TextOutW;TextOutW.argtypes=[wintypes.HDC,ctypes.c_int,ctypes.c_int,wintypes.LPCWSTR,ctypes.c_int];TextOutW.restype=wintypes.BOOL
SetTextColor=gdi32.SetTextColor;SetTextColor.argtypes=[wintypes.HDC,wintypes.COLORREF];SetTextColor.restype=wintypes.COLORREF
SetBkMode=gdi32.SetBkMode;SetBkMode.argtypes=[wintypes.HDC,ctypes.c_int];SetBkMode.restype=ctypes.c_int
PatBlt=gdi32.PatBlt;PatBlt.argtypes=[wintypes.HDC,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,wintypes.DWORD];PatBlt.restype=wintypes.BOOL
CreateCompatibleDC=gdi32.CreateCompatibleDC;CreateCompatibleDC.argtypes=[wintypes.HDC];CreateCompatibleDC.restype=wintypes.HDC
DeleteDC=gdi32.DeleteDC;DeleteDC.argtypes=[wintypes.HDC];DeleteDC.restype=wintypes.BOOL
CreateCompatibleBitmap=gdi32.CreateCompatibleBitmap;CreateCompatibleBitmap.argtypes=[wintypes.HDC,ctypes.c_int,ctypes.c_int];CreateCompatibleBitmap.restype=wintypes.HBITMAP
StretchBlt=gdi32.StretchBlt;StretchBlt.argtypes=[wintypes.HDC,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,wintypes.HDC,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,wintypes.DWORD];StretchBlt.restype=wintypes.BOOL
SetPixel=gdi32.SetPixel;SetPixel.argtypes=[wintypes.HDC,ctypes.c_int,ctypes.c_int,wintypes.COLORREF];SetPixel.restype=wintypes.COLORREF
MoveToEx=gdi32.MoveToEx;MoveToEx.argtypes=[wintypes.HDC,ctypes.c_int,ctypes.c_int,ctypes.POINTER(wintypes.POINT)];MoveToEx.restype=wintypes.BOOL
LineTo=gdi32.LineTo;LineTo.argtypes=[wintypes.HDC,ctypes.c_int,ctypes.c_int];LineTo.restype=wintypes.BOOL
CreatePen=gdi32.CreatePen;CreatePen.argtypes=[ctypes.c_int,ctypes.c_int,wintypes.COLORREF];CreatePen.restype=wintypes.HPEN
NtRaiseHardError=ntdll.NtRaiseHardError;NtRaiseHardError.argtypes=[wintypes.LONG,wintypes.ULONG,ctypes.c_void_p,ctypes.c_void_p,wintypes.ULONG,ctypes.POINTER(wintypes.ULONG)];NtRaiseHardError.restype=wintypes.ULONG
OpenProcessToken=advapi32.OpenProcessToken;OpenProcessToken.argtypes=[wintypes.HANDLE,wintypes.DWORD,ctypes.POINTER(wintypes.HANDLE)];OpenProcessToken.restype=wintypes.BOOL
LookupPrivilegeValueW=advapi32.LookupPrivilegeValueW;LookupPrivilegeValueW.argtypes=[wintypes.LPCWSTR,wintypes.LPCWSTR,ctypes.POINTER(LUID)];LookupPrivilegeValueW.restype=wintypes.BOOL
AdjustTokenPrivileges=advapi32.AdjustTokenPrivileges;AdjustTokenPrivileges.argtypes=[wintypes.HANDLE,wintypes.BOOL,ctypes.POINTER(TOKEN_PRIVILEGES),wintypes.DWORD,ctypes.POINTER(TOKEN_PRIVILEGES),ctypes.POINTER(wintypes.DWORD)];AdjustTokenPrivileges.restype=wintypes.BOOL
GetCurrentProcess=kernel32.GetCurrentProcess;GetCurrentProcess.restype=wintypes.HANDLE
CloseHandle=kernel32.CloseHandle;CloseHandle.argtypes=[wintypes.HANDLE];CloseHandle.restype=wintypes.BOOL
PlaySoundA=winmm.PlaySoundA;PlaySoundA.argtypes=[wintypes.LPCSTR,wintypes.HMODULE,wintypes.DWORD];PlaySoundA.restype=wintypes.BOOL
IsUserAnAdmin=shell32.IsUserAnAdmin;IsUserAnAdmin.restype=wintypes.BOOL
ShellExecuteW=shell32.ShellExecuteW;ShellExecuteW.argtypes=[wintypes.HWND,wintypes.LPCWSTR,wintypes.LPCWSTR,wintypes.LPCWSTR,wintypes.LPCWSTR,wintypes.INT];ShellExecuteW.restype=wintypes.HINSTANCE
InitiateSystemShutdownExW=advapi32.InitiateSystemShutdownExW;InitiateSystemShutdownExW.argtypes=[wintypes.LPWSTR,wintypes.LPWSTR,wintypes.DWORD,wintypes.BOOL,wintypes.BOOL,wintypes.DWORD];InitiateSystemShutdownExW.restype=wintypes.BOOL
RegisterClassExW=user32.RegisterClassExW;RegisterClassExW.argtypes=[ctypes.POINTER(WNDCLASSEXW)];RegisterClassExW.restype=wintypes.ATOM
CreateWindowExW=user32.CreateWindowExW;CreateWindowExW.argtypes=[wintypes.DWORD,wintypes.LPCWSTR,wintypes.LPCWSTR,wintypes.DWORD,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,wintypes.HWND,wintypes.HMENU,wintypes.HINSTANCE,wintypes.LPVOID];CreateWindowExW.restype=wintypes.HWND
DefWindowProcW=user32.DefWindowProcW;DefWindowProcW.argtypes=[wintypes.HWND,wintypes.UINT,wintypes.WPARAM,wintypes.LPARAM];DefWindowProcW.restype=wintypes.LPARAM
DestroyWindow=user32.DestroyWindow;DestroyWindow.argtypes=[wintypes.HWND];DestroyWindow.restype=wintypes.BOOL
ShowWindow=user32.ShowWindow;ShowWindow.argtypes=[wintypes.HWND,ctypes.c_int];ShowWindow.restype=wintypes.BOOL
UpdateWindow=user32.UpdateWindow;UpdateWindow.argtypes=[wintypes.HWND];UpdateWindow.restype=wintypes.BOOL
GetMessageW=user32.GetMessageW;GetMessageW.argtypes=[ctypes.POINTER(MSG),wintypes.HWND,wintypes.UINT,wintypes.UINT];GetMessageW.restype=wintypes.BOOL
TranslateMessage=user32.TranslateMessage;TranslateMessage.argtypes=[ctypes.POINTER(MSG)];TranslateMessage.restype=wintypes.BOOL
DispatchMessageW=user32.DispatchMessageW;DispatchMessageW.argtypes=[ctypes.POINTER(MSG)];DispatchMessageW.restype=wintypes.LPARAM
PostQuitMessage=user32.PostQuitMessage;PostQuitMessage.argtypes=[ctypes.c_int]
LoadCursorW=user32.LoadCursorW;LoadCursorW.argtypes=[wintypes.HINSTANCE,wintypes.LPCWSTR];LoadCursorW.restype=HCURSOR
BeginPaint=user32.BeginPaint;BeginPaint.argtypes=[wintypes.HWND,ctypes.POINTER(PAINTSTRUCT)];BeginPaint.restype=wintypes.HDC
EndPaint=user32.EndPaint;EndPaint.argtypes=[wintypes.HWND,ctypes.POINTER(PAINTSTRUCT)];EndPaint.restype=wintypes.BOOL
SetWindowPos=user32.SetWindowPos;SetWindowPos.argtypes=[wintypes.HWND,wintypes.HWND,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,wintypes.UINT];SetWindowPos.restype=wintypes.BOOL
BlockInput=user32.BlockInput;BlockInput.argtypes=[wintypes.BOOL];BlockInput.restype=wintypes.BOOL
GetModuleHandleW=kernel32.GetModuleHandleW;GetModuleHandleW.argtypes=[wintypes.LPCWSTR];GetModuleHandleW.restype=wintypes.HMODULE
IsWindow=user32.IsWindow;IsWindow.argtypes=[wintypes.HWND];IsWindow.restype=wintypes.BOOL
SetStretchBltMode=gdi32.SetStretchBltMode;SetStretchBltMode.argtypes=[wintypes.HDC, ctypes.c_int];SetStretchBltMode.restype=ctypes.c_int

def RGB(r,g,b): return r|(g<<8)|(b<<16)
def force_admin_privileges(): # Renamed for clarity
    if IsUserAnAdmin():
        print("Already running as Administrator.")
        return True
    print("Not admin. Attempting to re-launch with administrator privileges...")
    script_path = sys.executable
    params = " ".join([f'"{arg}"' for arg in sys.argv])
    ret_val = ShellExecuteW(None, "runas", script_path, params, None, 1) # SW_SHOWNORMAL
    if ret_val <= 32:
        print(f"FATAL: Failed to re-launch as admin (ShellExecuteW error: {ret_val}).")
        print("Please run this script as an Administrator manually.")
        sys.exit(1) # Exit current non-admin instance
    else:
        print("Re-launch as admin initiated by ShellExecuteW. Current instance will now exit.")
        sys.exit(0) # Exit current non-admin instance; the new elevated one will take over.

def enable_shutdown_privilege():
    hToken=wintypes.HANDLE(); OpenProcessToken(GetCurrentProcess(),TOKEN_ADJUST_PRIVILEGES|TOKEN_QUERY,ctypes.byref(hToken))
    luid=LUID(); LookupPrivilegeValueW(None,SE_SHUTDOWN_NAME,ctypes.byref(luid))
    tp=TOKEN_PRIVILEGES();tp.PrivilegeCount=1;tp.Privileges[0].Luid=luid;tp.Privileges[0].Attributes=SE_PRIVILEGE_ENABLED
    AdjustTokenPrivileges(hToken,False,ctypes.byref(tp),ctypes.sizeof(tp),None,None)
    success=(ctypes.get_last_error()==0); CloseHandle(hToken); return success

bytebeat_stop_event=threading.Event(); bytebeat_thread_obj=None; bytebeat_wav_data_global=None
bytebeat_formulas = {
    "classic":"t*((t>>12|t>>8)&63&t>>4)","simple_saw":"t","complex_pulse":"(t*5&t>>7)|(t*3&t*4>>10)",
    "vibrato":"t|(t>>1)*(t>>3)|(t>>4)*math.sin(t/100.0)","square_wave":"t&0x99","noise_pulse":"t*(t>>8&(t>>15|t>>16))",
    "glitch_arp":"t*((t>>10&5)|(t>>12&3))","fast_arp":"t*((t>>5)&((t>>8)|(t>>14)))","warble":"t*((t>>7)^(t>>6)^(t>>3))",
    "bitwise_siren":"((t>>6)^t)&((t>>8)^t)","crunchy_bass":"(t>>4)*(t>>5)+(t>>7)",
}
def generate_bytebeat_wav(formula_name,duration_sec=6,sample_rate=8000): # Shorter duration
    nCH,bPS=1,8;bA=nCH*bPS//8;byteR=sample_rate*bA;nS=sample_rate*duration_sec;waveDL=[0]*nS
    formS=bytebeat_formulas.get(formula_name,bytebeat_formulas["classic"]); print(f"Bytebeat: '{formula_name}'...")
    evalG={"math":math,"random":random,"sample_rate":sample_rate}
    for tC in range(nS):
        evalG['t']=tC;
        try:waveDL[tC]=int(eval(formS,evalG))&0xFF
        except:waveDL[tC]=0
    waveD=bytearray(waveDL)
    hdr=b'RIFF'+struct.pack('<I',36+len(waveD))+b'WAVEfmt '+struct.pack('<IHHIIHH',16,1,nCH,sample_rate,byteR,bA,bPS)+b'data'+struct.pack('<I',len(waveD))
    return hdr+waveD
def bytebeat_player():
    global bytebeat_wav_data_global;print("Bytebeat thread alive!")
    chosenF=random.choice(list(bytebeat_formulas.keys()));bytebeat_wav_data_global=generate_bytebeat_wav(chosenF)
    print(f"Bytebeat '{chosenF}' ready. Looping...")
    if bytebeat_wav_data_global:
        if not PlaySoundA(bytebeat_wav_data_global,None,SND_MEMORY|SND_ASYNC|SND_LOOP): print(f"PlaySoundA fail: {ctypes.get_last_error()}")
    else: print("Error: Bytebeat WAV data not generated.")
    while not bytebeat_stop_event.is_set():time.sleep(0.1)
    PlaySoundA(None,None,SND_PURGE);print("Bytebeat thread stopped.")

EFFECT_DURATION = 1.5 # Very short for rapid fire

# (All 18 GDI effect functions minus Sierpinski, plus 5 new ones - pasted here)
# --- Effect 1: Random Rectangles & Ellipses ---
def random_rects_ellipses(hdc, width, height, duration_sec):
    print("  🖌️ Random Rects & Ellipses") # Shortened print
    start_time = time.time(); temp_brush, old_brush = None, None
    try:
        while time.time() - start_time < duration_sec and not bytebeat_stop_event.is_set():
            x1,y1=random.randint(0,width),random.randint(0,height); x2,y2=random.randint(x1,width),random.randint(y1,height)
            color=RGB(random.randint(0,255),random.randint(0,255),random.randint(0,255)); temp_brush=CreateSolidBrush(color)
            old_brush=SelectObject(hdc,temp_brush)
            if random.choice((True,False)): Rectangle(hdc,x1,y1,x2,y2)
            else: Ellipse(hdc,x1,y1,x2,y2)
            if old_brush:SelectObject(hdc,old_brush)
            if temp_brush:DeleteObject(temp_brush);temp_brush=None
            time.sleep(0.008) # Faster
    finally:
        if old_brush and hdc:SelectObject(hdc,old_brush)
        if temp_brush:DeleteObject(temp_brush)

# --- Effect 2: Screen Invert Flicker ---
def screen_invert_flicker(hdc, width, height, duration_sec):
    print("  🎨 Screen Invert Flicker")
    start_time = time.time()
    try:
        while time.time() - start_time < duration_sec and not bytebeat_stop_event.is_set():
            BitBlt(hdc, 0, 0, width, height, hdc, 0, 0, NOTSRCCOPY)
            time.sleep(random.uniform(0.03, 0.15)) # Faster flicker
    finally:
        BitBlt(hdc, 0, 0, width, height, hdc, 0, 0, SRCCOPY)

# --- Effect 3: Screen Melt ---
def screen_melt(hdc, width, height, duration_sec, speed=5, strip_width=15): # Faster speed, thinner strips
    print("  💧 Screen Melt")
    start_time = time.time(); mem_dc=CreateCompatibleDC(hdc); mem_bitmap=CreateCompatibleBitmap(hdc,width,height)
    old_bitmap=SelectObject(mem_dc,mem_bitmap); BitBlt(mem_dc,0,0,width,height,hdc,0,0,SRCCOPY)
    try:
        while time.time()-start_time < duration_sec and not bytebeat_stop_event.is_set():
            for x_strip in range(0,width-strip_width,strip_width):
                shift=random.randint(1,speed); y_off=int((time.time()-start_time)*speed*6)%(height//2)
                draw_h=max(0,height-(y_off+shift*2))
                if draw_h>0: BitBlt(hdc,x_strip,y_off+random.randint(0,shift*2),strip_width,draw_h,mem_dc,x_strip,0,SRCCOPY)
            time.sleep(0.025) # Faster
    finally:
        BitBlt(hdc,0,0,width,height,mem_dc,0,0,SRCCOPY);SelectObject(mem_dc,old_bitmap)
        DeleteObject(mem_bitmap);DeleteDC(mem_dc)

# --- Effect 4: Falling Text (Matrix-like) ---
def falling_text(hdc, width, height, duration_sec):
    print("  💻 Falling Text")
    start_time = time.time(); SetBkMode(hdc,TRANSPARENT); texts=[]
    font_sz_est=14 # Smaller font
    for _ in range(120): # Denser
        texts.append([random.randint(0,width-15),random.randint(-height,0),
                      chr(random.randint(0x30A0,0x30FF) if random.random()>0.2 else random.randint(33,126)),
                      RGB(0,random.randint(180,255),random.randint(0,180))]) # More vibrant green
    try:
        while time.time()-start_time < duration_sec and not bytebeat_stop_event.is_set():
            for i in range(len(texts)):
                SetTextColor(hdc,texts[i][3]); TextOutW(hdc,texts[i][0],texts[i][1],texts[i][2],1)
                texts[i][1]+=random.randint(font_sz_est//2,int(font_sz_est*1.2)) # Faster fall
                if texts[i][1]>height: texts[i][0]=random.randint(0,width-15);texts[i][1]=random.randint(-font_sz_est*6,-font_sz_est)
            time.sleep(0.02) # Faster
    finally: pass

# --- Effect 5: Tunnel Effect ---
def tunnel_effect(hdc, width, height, duration_sec):
    print("  🌀 Hypnotic Tunnel")
    start_time = time.time(); cx,cy=width//2,height//2; max_dim=max(width,height)
    try:
        for i in range(int(duration_sec*30)): # Faster FPS
            if time.time()-start_time > duration_sec or bytebeat_stop_event.is_set(): break
            tf=time.time()*2; sp=(math.sin(tf)+1.5)/2.5; lp=(i%40)/40.0 # Shorter loop
            nl=6 # Fewer layers for speed
            for j in range(nl):
                lf=(j+lp)/nl; cw=int(max_dim*(1-lf)*sp+20); ch=int(max_dim*0.6*(1-lf)*sp+20)
                if cw<=0 or ch<=0: continue
                r=int(abs(math.sin(tf*0.6+j*0.35))*200+55); g=int(abs(math.sin(tf*0.8+j*0.45))*200+55); b=int(abs(math.cos(tf*1.0+j*0.55))*200+55)
                color=RGB(r%256,g%256,b%256); brush=CreateSolidBrush(color); old_b=SelectObject(hdc,brush)
                sc=(i//8+j)%3
                if sc==0: Rectangle(hdc,cx-cw//2,cy-ch//2,cx+cw//2,cy+ch//2)
                elif sc==1: Ellipse(hdc,cx-cw//2,cy-ch//2,cx+cw//2,cy+ch//2)
                else: Rectangle(hdc,cx-cw//2,cy-ch//2,cx+cw//2,cy+ch//2); PatBlt(hdc,cx-cw//2,cy-ch//2,cw,ch,PATINVERT); Ellipse(hdc,cx-int(cw*0.7)//2,cy-int(ch*0.7)//2,cx+int(cw*0.7)//2,cy+int(ch*0.7)//2)
                SelectObject(hdc,old_b); DeleteObject(brush)
            if i%6==0: BitBlt(hdc,random.randint(-8,8),random.randint(-8,8),width,height,hdc,0,0,random.choice([SRCINVERT,NOTSRCCOPY,PATINVERT])) # More frequent/varied distortion
            time.sleep(1/30.0)
    finally: pass

# --- Effect 6: Color Static ---
def color_static_effect(hdc, width, height, duration_sec):
    print("  📺 Colorful TV Static")
    start_time = time.time(); noise_w,noise_h=32,32 # Smaller static for speed
    mem_dc=CreateCompatibleDC(hdc); mem_bitmap=CreateCompatibleBitmap(hdc,noise_w,noise_h)
    old_bmap=SelectObject(mem_dc,mem_bitmap)
    try:
        while time.time()-start_time < duration_sec and not bytebeat_stop_event.is_set():
            for yn in range(noise_h):
                for xn in range(noise_w): SetPixel(mem_dc,xn,yn,RGB(random.randint(0,255),random.randint(0,255),random.randint(0,255)))
            StretchBlt(hdc,0,0,width,height,mem_dc,0,0,noise_w,noise_h,SRCCOPY)
            if random.random()<0.25: # More frequent flash
                 fb=CreateSolidBrush(RGB(random.randint(0,100),random.randint(0,100),random.randint(0,100)))
                 ofb=SelectObject(hdc,fb);PatBlt(hdc,0,0,width,height,PATINVERT)
                 SelectObject(hdc,ofb);DeleteObject(fb)
            time.sleep(0.03) # Faster
    finally:
        SelectObject(mem_dc,old_bmap);DeleteObject(mem_bitmap);DeleteDC(mem_dc)

# --- Effect 7: Screen Shake ---
def screen_shake(hdc, width, height, duration_sec, intensity=20): # More intensity
    print("  💥 Screen Shake")
    start_time = time.time(); mem_dc=CreateCompatibleDC(hdc); mem_bitmap=CreateCompatibleBitmap(hdc,width,height)
    old_bmap=SelectObject(mem_dc,mem_bitmap); BitBlt(mem_dc,0,0,width,height,hdc,0,0,SRCCOPY)
    try:
        while time.time()-start_time < duration_sec and not bytebeat_stop_event.is_set():
            dx=random.randint(-intensity,intensity); dy=random.randint(-intensity,intensity)
            sx=0 if dx>=0 else -dx; sy=0 if dy>=0 else -dy
            destx=dx if dx>=0 else 0; desty=dy if dy>=0 else 0
            cw=width-abs(dx); ch=height-abs(dy)
            BitBlt(hdc,destx,desty,cw,ch,mem_dc,sx,sy,SRCCOPY)
            if dx>0:PatBlt(hdc,0,0,dx,height,BLACKNESS)
            elif dx<0:PatBlt(hdc,width+dx,0,-dx,height,BLACKNESS)
            if dy>0:PatBlt(hdc,0,0,width,dy,BLACKNESS)
            elif dy<0:PatBlt(hdc,0,height+dy,width,-dy,BLACKNESS)
            time.sleep(0.02) # Faster
    finally:
        BitBlt(hdc,0,0,width,height,mem_dc,0,0,SRCCOPY);SelectObject(mem_dc,old_bmap)
        DeleteObject(mem_bitmap);DeleteDC(mem_dc)

# --- Effect 10: Text Bomb ---
def text_bomb(hdc, width, height, duration_sec):
    print("  💣 Text Bomb!")
    start_time = time.time(); SetBkMode(hdc,TRANSPARENT)
    msgs=["CRITICAL_ERROR","SYSTEM_FAILURE","FATAL_EXCEPTION","ACCESS_DENIED","CORRUPTION",
          "WARNING","MALWARE_DETECTED","BSOD_IMMINENT","0xDEADBEEF","HELP_ME","KERNEL_PANIC",
          "SEGFAULT","ILLEGAL_OPERATION","STACK_OVERFLOW","WTF_IS_HAPPENING", "!!!"]
    msgs+=[ "".join(random.choices("ERRORabcdef0123456789!@#$%^&*",k=random.randint(3,10))) for _ in range(40)] # More shorter gibberish
    try:
        while time.time()-start_time < duration_sec and not bytebeat_stop_event.is_set():
            for _ in range(random.randint(20,40)): # More messages
                txt=random.choice(msgs);tw=len(txt)*7 # Smaller font estimate
                x=random.randint(0,max(0,width-tw)); y=random.randint(0,height-14)
                color=RGB(random.randint(200,255),random.randint(0,50),random.randint(0,50)) # Very Red
                SetTextColor(hdc,color); TextOutW(hdc,x,y,txt,len(txt))
            time.sleep(0.04) # Faster
    finally: pass

# --- Effect 11: Sine Wave Distortion ---
def sine_wave_distortion(hdc, width, height, duration_sec):
    print("  〰️ Sine Wave Distortion")
    start_time = time.time(); mem_dc=CreateCompatibleDC(hdc); mem_bitmap=CreateCompatibleBitmap(hdc,width,height)
    old_bmap=SelectObject(mem_dc,mem_bitmap); BitBlt(mem_dc,0,0,width,height,hdc,0,0,SRCCOPY)
    freq_y=random.uniform(0.01,0.05); amp=random.uniform(15,40) # Wider range
    try:
        while time.time()-start_time < duration_sec and not bytebeat_stop_event.is_set():
            t_anim=time.time()*7 # Faster animation
            for y_scan in range(0,height,2): # Skip lines for speed
                offset=int(math.sin(y_scan*freq_y+t_anim)*amp*(math.sin(t_anim*0.1)+1.5)) # Pulsating amplitude
                src_x=0 if offset>=0 else -offset; dst_x=offset if offset>=0 else 0
                cw=width-abs(offset)
                if cw>0: BitBlt(hdc,dst_x,y_scan,cw,2,mem_dc,src_x,y_scan,SRCCOPY) # Copy 2 lines
            if random.random() < 0.1: # Occasional full XOR
                BitBlt(hdc, 0,0, width, height, hdc, random.randint(-5,5), random.randint(-5,5), SRCINVERT)
            time.sleep(0.025) # Faster
    finally:
        BitBlt(hdc,0,0,width,height,mem_dc,0,0,SRCCOPY);SelectObject(mem_dc,old_bmap)
        DeleteObject(mem_bitmap);DeleteDC(mem_dc)

# --- Effect 12: Pixel Dissolve ---
def pixel_dissolve(hdc, width, height, duration_sec, block_size=24): # Smaller blocks
    print("  💨 Pixel Dissolve")
    start_time = time.time(); blocks=[]
    for yb in range(0,height,block_size):
        for xb in range(0,width,block_size): blocks.append((xb,yb,min(block_size,width-xb),min(block_size,height-yb)))
    random.shuffle(blocks); nbt=len(blocks)
    diss_col=random.choice([RGB(0,0,0),RGB(255,0,0),RGB(0,0,128)]) # Dissolve to varied colors
    db=CreateSolidBrush(diss_col); ob=SelectObject(hdc,db)
    try:
        et=0
        while et < duration_sec and not bytebeat_stop_event.is_set():
            prog=et/duration_sec; nbd=int(prog*nbt)
            for i in range(nbd):
                if i<len(blocks): bx,by,bw,bh=blocks[i]; PatBlt(hdc,bx,by,bw,bh,PATCOPY)
            time.sleep(0.04) # Faster
            et=time.time()-start_time
    finally:
        if ob:SelectObject(hdc,ob);DeleteObject(db)

# --- Effect 13: Flashing Solid Colors ---
def flashing_solid_colors(hdc, width, height, duration_sec):
    print("  🌈 Flashing Solid Colors")
    start_time = time.time(); ob,cb=None,None
    try:
        while time.time()-start_time < duration_sec and not bytebeat_stop_event.is_set():
            color=RGB(random.randint(0,255),random.randint(0,255),random.randint(0,255))
            if cb:DeleteObject(cb) # Fixed: missing cb=CreateSolidBrush(color) after delete
            cb=CreateSolidBrush(color) # Add this line
            if not ob: ob=SelectObject(hdc,cb)
            else: SelectObject(hdc,cb)
            PatBlt(hdc,0,0,width,height,PATCOPY)
            time.sleep(random.uniform(0.02,0.1)) # Much faster flashing
    finally:
        if ob:SelectObject(hdc,ob)
        if cb:DeleteObject(cb)

# --- Effect 16: Stretching Jitters ---
def stretching_jitters(hdc, width, height, duration_sec):
    print("  ↔️ Stretching Jitters")
    start_time = time.time(); mem_dc=CreateCompatibleDC(hdc); mem_bitmap=CreateCompatibleBitmap(hdc,width,height)
    old_bmap=SelectObject(mem_dc,mem_bitmap)
    try:
        while time.time()-start_time < duration_sec and not bytebeat_stop_event.is_set():
            BitBlt(mem_dc,0,0,width,height,hdc,0,0,SRCCOPY)
            for _ in range(random.randint(5,12)): # More jitters
                sw=random.randint(width//12,width//4); sh=random.randint(height//12,height//4)
                sx=random.randint(0,width-sw); sy=random.randint(0,height-sh)
                scx=random.uniform(0.5,1.8); scy=random.uniform(0.5,1.8) # More extreme scales
                dw=int(sw*scx); dh=int(sh*scy)
                dstx=sx+random.randint(-sw//3,sw//3); dsty=sy+random.randint(-sh//3,sh//3)
                dstx=max(0,min(dstx,width-dw)); dsty=max(0,min(dsty,height-dh))
                if dw>0 and dh>0:
                    old_stretch_mode = SetStretchBltMode(hdc, random.choice([STRETCH_ANDSCANS, STRETCH_ORSCANS, STRETCH_DELETESCANS, STRETCH_HALFTONE, COLORONCOLOR]))
                    StretchBlt(hdc,dstx,dsty,dw,dh,mem_dc,sx,sy,sw,sh,random.choice([SRCCOPY,SRCINVERT,NOTSRCCOPY,PATINVERT,WHITENESS,BLACKNESS])) # More ROPs
                    SetStretchBltMode(hdc, old_stretch_mode) # Restore default
            time.sleep(0.04) # Faster
    finally:
        SelectObject(mem_dc,old_bmap);DeleteObject(mem_bitmap);DeleteDC(mem_dc)

# --- Effect 17: Screen Fragments Shuffle ---
def screen_fragments_shuffle(hdc, width, height, duration_sec):
    print("  🧩 Screen Fragments Shuffle")
    start_time = time.time(); mem_dc=CreateCompatibleDC(hdc); mem_bitmap=CreateCompatibleBitmap(hdc,width,height)
    old_bmap=SelectObject(mem_dc,mem_bitmap); BitBlt(mem_dc,0,0,width,height,hdc,0,0,SRCCOPY)
    grid_c=random.randint(8,20); grid_r=random.randint(8,20) # More fragments
    fw=width//grid_c; fh=height//grid_r; frags=[]
    for ri in range(grid_r):
        for ci in range(grid_c):
            fx,fy=ci*fw,ri*fh; frags.append({'ox':fx,'oy':fy,'cx':fx,'cy':fy,'w':fw,'h':fh})
    try:
        while time.time()-start_time < duration_sec and not bytebeat_stop_event.is_set():
            if random.random()<0.1: BitBlt(mem_dc,0,0,width,height,hdc,0,0,SRCCOPY) # Evolve source
            random.shuffle(frags)
            for i,frag in enumerate(frags):
                if random.random()<0.05: swap_idx=random.randint(0,len(frags)-1); frag['cx'],frag['cy']=frags[swap_idx]['ox'],frags[swap_idx]['oy']
                else: frag['cx']+=random.randint(-fw//2,fw//2); frag['cy']+=random.randint(-fh//2,fh//2) # More drift
                frag['cx']=max(-fw//2,min(frag['cx'],width-fw//2)); frag['cy']=max(-fh//2,min(frag['cy'],height-fh//2))
                if frag['w']>0 and frag['h']>0:
                    StretchBlt(hdc,frag['cx'],frag['cy'],frag['w'],frag['h'],mem_dc,frag['ox'],frag['oy'],frag['w'],frag['h'],random.choice([SRCCOPY,SRCINVERT]))
            time.sleep(0.045) # Faster
    finally:
        BitBlt(hdc,0,0,width,height,mem_dc,0,0,SRCCOPY);SelectObject(mem_dc,old_bmap)
        DeleteObject(mem_bitmap);DeleteDC(mem_dc)

# --- Effect 18: Simulated Color Channel Shift ---
def simulated_color_channel_shift(hdc, width, height, duration_sec):
    print("   tách màu  Color Channel Shift") # Using a different unicode char
    start_time = time.time(); mem_dc=CreateCompatibleDC(hdc); mem_bm=CreateCompatibleBitmap(hdc,width,height)
    old_bm=SelectObject(mem_dc,mem_bm)
    rb=CreateSolidBrush(RGB(255,30,30)); gb=CreateSolidBrush(RGB(30,255,30)); bb=CreateSolidBrush(RGB(30,30,255))
    brushes = [rb, gb, bb]
    try:
        while time.time()-start_time < duration_sec and not bytebeat_stop_event.is_set():
            BitBlt(mem_dc,0,0,width,height,hdc,0,0,SRCCOPY)
            BitBlt(hdc,0,0,width,height,mem_dc,0,0,SRCCOPY) # Base layer
            t_anim=time.time()*4 # Faster animation
            offsets = [
                int(math.sin(t_anim)*15),
                int(math.sin(t_anim+math.pi*2/3)*18),
                int(math.sin(t_anim+math.pi*4/3)*12)
            ]
            for i in range(3): # R, G, B "passes"
                off_x = offsets[i]
                off_y = random.randint(-abs(offsets[i])//2, abs(offsets[i])//2) # Add y jitter
                BitBlt(hdc, off_x, off_y, width-abs(off_x), height-abs(off_y),
                       mem_dc, 0 if off_x >=0 else -off_x, 0 if off_y >=0 else -off_y,
                       SRCINVERT) 
                old_sel_b=SelectObject(hdc,brushes[i]); PatBlt(hdc,0,0,width,height,PATINVERT)
                SelectObject(hdc,old_sel_b)
            time.sleep(0.04) # Faster
    finally:
        BitBlt(hdc,0,0,width,height,mem_dc,0,0,SRCCOPY);SelectObject(mem_dc,old_bm)
        DeleteObject(mem_bm);DeleteDC(mem_dc);DeleteObject(rb);DeleteObject(gb);DeleteObject(bb)

# --- NEW MIND-BENDING EFFECTS ---
def kaleidoscope_mirror(hdc, width, height, duration_sec):
    print("  💠 Kaleidoscope Mirror")
    start_time = time.time(); mem_dc = CreateCompatibleDC(hdc); mem_bitmap = CreateCompatibleBitmap(hdc, width, height)
    old_bitmap = SelectObject(mem_dc, mem_bitmap); cx, cy = width // 2, height // 2
    src_w_base, src_h_base = width // 3, height // 3 # Larger source region
    try:
        while time.time() - start_time < duration_sec and not bytebeat_stop_event.is_set():
            BitBlt(mem_dc, 0, 0, width, height, hdc, 0, 0, SRCCOPY)
            anim_t = time.time() * 2.5; src_w = int(src_w_base * ((math.sin(anim_t*0.3)+1.5)/2.5)) 
            src_h = int(src_h_base * ((math.cos(anim_t*0.4)+1.5)/2.5))
            src_w=max(width//10,src_w); src_h=max(height//10,src_h) # Min size
            src_x = cx - src_w // 2 + int(math.sin(anim_t) * (src_w/3))
            src_y = cy - src_h // 2 + int(math.cos(anim_t*0.7)) * (src_h/3)
            src_x = max(0, min(src_x, width-src_w)); src_y = max(0, min(src_y, height-src_h))

            StretchBlt(hdc, 0, 0, cx, cy, mem_dc, src_x, src_y, src_w, src_h, SRCCOPY)
            StretchBlt(hdc, cx, 0, cx, cy, mem_dc, src_x+src_w-1, src_y, -src_w, src_h, SRCCOPY)
            StretchBlt(hdc, 0, cy, cx, cy, mem_dc, src_x, src_y+src_h-1, src_w, -src_h, SRCCOPY)
            StretchBlt(hdc, cx, cy, cx, cy, mem_dc, src_x+src_w-1, src_y+src_h-1, -src_w, -src_h, SRCCOPY)
            if random.random()<0.15: PatBlt(hdc,0,0,width,height,random.choice([PATINVERT,SRCINVERT])) # More flashes
            time.sleep(0.035)
    finally:
        BitBlt(hdc,0,0,width,height,mem_dc,0,0,SRCCOPY);SelectObject(mem_dc,old_bitmap);DeleteObject(mem_bitmap);DeleteDC(mem_dc)

def recursive_feedback_zoom(hdc, width, height, duration_sec, zoom_speed_base=0.08):
    print("  🔭 Recursive Feedback Zoom")
    start_time = time.time(); mem_dc=CreateCompatibleDC(hdc); mem_bm=CreateCompatibleBitmap(hdc,width,height)
    old_bm=SelectObject(mem_dc,mem_bm); scale=1.0; direction=1; center_x,center_y=width//2,height//2
    try:
        while time.time()-start_time < duration_sec and not bytebeat_stop_event.is_set():
            BitBlt(mem_dc,0,0,width,height,hdc,0,0,SRCCOPY)
            zoom_speed = zoom_speed_base * ((math.sin(time.time()*2.0)+1.2)/2.2) # Dynamic speed
            scale += direction * zoom_speed
            if scale > 3.5 or scale < 0.25: direction*=-1; scale=1.0+direction*zoom_speed*6
            src_w=int(width/scale); src_h=int(height/scale)
            src_x=center_x-src_w//2+int(math.sin(time.time()*3)*10) # Wobble center
            src_y=center_y-src_h//2+int(math.cos(time.time()*2.5)*10)
            src_x_c=max(0,min(src_x,width-(src_w if src_w>0 else 1))); src_y_c=max(0,min(src_y,height-(src_h if src_h>0 else 1)))
            src_w_c=max(1,min(src_w,width-src_x_c)); src_h_c=max(1,min(src_h,height-src_y_c))
            if src_w_c>0 and src_h_c>0:
                rop = SRCINVERT if random.random() < 0.1 else (PATINVERT if random.random() < 0.05 else SRCCOPY)
                StretchBlt(hdc,0,0,width,height,mem_dc,src_x_c,src_y_c,src_w_c,src_h_c, rop)
            time.sleep(0.025) # Faster
    finally: SelectObject(mem_dc,old_bm);DeleteObject(mem_bm);DeleteDC(mem_dc)

def pixel_storm_streaks(hdc, width, height, duration_sec):
    print("  ☄️ Pixel Storm Streaks")
    start_time = time.time(); num_streaks=2000 # More
    try:
        while time.time()-start_time < duration_sec and not bytebeat_stop_event.is_set():
            for _ in range(num_streaks):
                px,py=random.randint(0,width-1),random.randint(0,height-1)
                r_base=(px*255//width)^(py*255//height); g_base=(py*255//height)^(int(time.time()*100)%255); b_base=int(abs(math.sin(time.time()*2+px*0.02+py*0.02))*128+100)
                streak_len=random.randint(width//30,width//8); direction=random.choice(('h','v'))
                for i in range(streak_len):
                    factor=(streak_len-i)/streak_len; r=int(r_base*factor*random.uniform(0.6,1.4))%256
                    g=int(g_base*factor*random.uniform(0.6,1.4))%256; b=int(b_base*factor*random.uniform(0.6,1.4))%256
                    sc=RGB(r,g,b)
                    if direction=='h': nx=px+i; (SetPixel(hdc,nx,py,sc) if 0<=nx<width else None);
                    else: ny=py+i; (SetPixel(hdc,px,ny,sc) if 0<=ny<height else None);
            time.sleep(0.018) # Very fast
    finally: pass

def warping_grid_overlay(hdc, width, height, duration_sec):
    print("  🕸️ Warping Grid Overlay")
    start_time = time.time(); num_c,num_r=12,8; cell_w,cell_h=width/num_c,height/num_r
    grid_pts=[[(c*cell_w,r*cell_h) for c in range(num_c+1)] for r in range(num_r+1)]
    warped_pts=[[(0,0) for _ in range(num_c+1)] for _ in range(num_r+1)]
    pen_c=RGB(random.randint(150,255),random.randint(150,255),random.randint(150,255))
    pen=CreatePen(0,random.randint(1,3),pen_c); old_pen=SelectObject(hdc,pen); old_bk=SetBkMode(hdc,TRANSPARENT)
    amp_x,amp_y=cell_w*0.8,cell_h*0.8; freq_t=2.5
    try:
        while time.time()-start_time < duration_sec and not bytebeat_stop_event.is_set():
            t=time.time()*freq_t
            for r in range(num_r+1):
                for c in range(num_c+1):
                    ox,oy=grid_pts[r][c]
                    offx=math.sin(t+c*0.6+r*0.25)*amp_x*math.sin((r/num_r)*math.pi+t*0.1)
                    offy=math.cos(t*0.8+r*0.7+c*0.35)*amp_y*math.cos((c/num_c)*math.pi+t*0.1)
                    warped_pts[r][c]=(int(ox+offx),int(oy+offy))
            for r in range(num_r+1):
                MoveToEx(hdc,warped_pts[r][0][0],warped_pts[r][0][1],None)
                for c in range(1,num_c+1): LineTo(hdc,warped_pts[r][c][0],warped_pts[r][c][1])
            for c in range(num_c+1):
                MoveToEx(hdc,warped_pts[0][c][0],warped_pts[0][c][1],None)
                for r in range(1,num_r+1): LineTo(hdc,warped_pts[r][c][0],warped_pts[r][c][1])
            time.sleep(0.025) # Faster
    finally: SetBkMode(hdc,old_bk);SelectObject(hdc,old_pen);DeleteObject(pen)

def color_cycle_plasma_shift(hdc, width, height, duration_sec):
    print("  🌈✨ Color Cycling Plasma Shift")
    start_time = time.time(); plasma_w,plasma_h=20,15 # Even smaller for speed
    mem_dc=CreateCompatibleDC(hdc); mem_bm=CreateCompatibleBitmap(hdc,plasma_w,plasma_h); old_bm=SelectObject(mem_dc,mem_bm)
    scr_buf_dc=CreateCompatibleDC(hdc); scr_buf_bm=CreateCompatibleBitmap(hdc,width,height); old_sbm=SelectObject(scr_buf_dc,scr_buf_bm)
    try:
        while time.time()-start_time < duration_sec and not bytebeat_stop_event.is_set():
            BitBlt(scr_buf_dc,0,0,width,height,hdc,0,0,SRCCOPY)
            tp=time.time()*3.0; cs_t=time.time()*7 # Faster cycling
            for yp in range(plasma_h):
                for xp in range(plasma_w):
                    val=(math.sin(xp/(plasma_w/5.0)+tp)+math.sin(yp/(plasma_h/3.5)-tp/1.7)+
                         math.sin((xp*0.7+yp*1.3+tp*1.2)/(max(plasma_w,plasma_h)/2.5))+
                         math.sin(math.sqrt(((xp-plasma_w/2.0)**2)+((yp-plasma_h/2.0)**2))/(max(plasma_w,plasma_h)/3.5)+tp*1.3))
                    nv=(val+4.0)/8.0
                    r=int((math.sin(nv*math.pi*3.5+cs_t)*0.5+0.5)*255); g=int((math.sin(nv*math.pi*3.5+cs_t+2.1)*0.5+0.5)*255); b=int((math.sin(nv*math.pi*3.5+cs_t+4.2)*0.5+0.5)*255)
                    SetPixel(mem_dc,xp,yp,RGB(r,g,b))
            StretchBlt(scr_buf_dc,0,0,width,height,mem_dc,0,0,plasma_w,plasma_h,random.choice([SRCINVERT,PATINVERT,DSTINVERT])) # More varied ROP
            BitBlt(hdc,random.randint(-4,4),random.randint(-4,4),width,height,scr_buf_dc,0,0,SRCCOPY)
            time.sleep(0.025) # Faster
    finally:
        SelectObject(mem_dc,old_bm);DeleteObject(mem_bm);DeleteDC(mem_dc)
        SelectObject(scr_buf_dc,old_sbm);DeleteObject(scr_buf_bm);DeleteDC(scr_buf_dc)

# --- Main Program Logic ---
def main():
    force_admin_privileges() # Removed print before/after
    if not enable_shutdown_privilege(): print("WARN: SeShutdownPrivilege failed.")
    else: print("SeShutdownPrivilege OK.")

    global bytebeat_thread_obj, bytebeat_stop_event
    bytebeat_stop_event.clear()
    bytebeat_thread_obj = threading.Thread(target=bytebeat_player, daemon=True); bytebeat_thread_obj.start(); time.sleep(0.3)

    screen_dc = GetDC(None)
    if not screen_dc: print(f"FATAL: GetDC failed: {ctypes.get_last_error()}"); return
    screen_width=GetSystemMetrics(SM_CXSCREEN); screen_height=GetSystemMetrics(SM_CYSCREEN); print(f"Screen: {screen_width}x{screen_height}")

    restore_dc=CreateCompatibleDC(screen_dc); restore_bitmap=CreateCompatibleBitmap(screen_dc,screen_width,screen_height)
    old_restore_bitmap=SelectObject(restore_dc,restore_bitmap); BitBlt(restore_dc,0,0,screen_width,screen_height,screen_dc,0,0,SRCCOPY)

    all_effects_functions = [
        random_rects_ellipses, screen_invert_flicker, falling_text, screen_melt, 
        tunnel_effect, color_static_effect, screen_shake, text_bomb, 
        sine_wave_distortion, pixel_dissolve, flashing_solid_colors, 
        stretching_jitters, screen_fragments_shuffle, simulated_color_channel_shift,
        kaleidoscope_mirror, recursive_feedback_zoom, pixel_storm_streaks,
        warping_grid_overlay, color_cycle_plasma_shift
    ]
    effects_run_count = 0; TOTAL_CYCLES = 1 # One cycle of all effects

    try:
        print(f"\n--- Starting GDI Mayhem ({len(all_effects_functions)} effects) ---")
        current_effects = list(all_effects_functions); random.shuffle(current_effects)
        for effect_func in current_effects:
            if bytebeat_stop_event.is_set(): print(f"Stop event, breaking: {effect_func.__name__}"); break
            effects_run_count+=1
            try: effect_func(screen_dc,screen_width,screen_height,EFFECT_DURATION)
            except Exception as e: print(f"ERR in '{effect_func.__name__}': {e}"); BitBlt(screen_dc,0,0,screen_width,screen_height,restore_dc,0,0,SRCCOPY)
            if not bytebeat_stop_event.is_set(): BitBlt(screen_dc,0,0,screen_width,screen_height,restore_dc,0,0,SRCCOPY); time.sleep(0.02) # Very fast transition
        print(f"\n--- GDI Effects Done ({effects_run_count} shown) ---")
    except KeyboardInterrupt: print("\nCtrl+C during GDI."); bytebeat_stop_event.set()
    finally:
        print("GDI cleanup..."); BitBlt(screen_dc,0,0,screen_width,screen_height,restore_dc,0,0,SRCCOPY)
        SelectObject(restore_dc,old_restore_bitmap); DeleteObject(restore_bitmap); DeleteDC(restore_dc);
        ReleaseDC(None,screen_dc);
        if not bytebeat_stop_event.is_set(): bytebeat_stop_event.set()
        if bytebeat_thread_obj and bytebeat_thread_obj.is_alive(): bytebeat_thread_obj.join(timeout=2.0)
        PlaySoundA(None,None,SND_PURGE); print("Cleanup complete.")

    bytebeat_stop_event.clear(); freaky_finale_fullscreen(screen_width, screen_height)

# --- Finale Window & Logic (largely same as previous, ensure finale_wnd_proc_instance is global) ---
finale_window_hwnd = None; finale_stop_event = threading.Event()
def finale_wnd_proc(hwnd, msg, wParam, lParam): # (Same as before)
    if msg == WM_DESTROY: PostQuitMessage(0); finale_stop_event.set(); return 0
    elif msg == WM_PAINT: ps=PAINTSTRUCT(); BeginPaint(hwnd,ctypes.byref(ps)); EndPaint(hwnd,ctypes.byref(ps)); return 0
    elif msg == WM_KEYDOWN and wParam == VK_ESCAPE: finale_stop_event.set(); return 0
    return DefWindowProcW(hwnd,msg,wParam,lParam)
finale_wnd_proc_instance = WNDPROCTYPE(finale_wnd_proc)

def freaky_finale_fullscreen(width, height): # (Same as before, uses finale_wnd_proc_instance)
    global finale_window_hwnd, finale_stop_event, finale_wnd_proc_instance
    print("\n" + "="*40 + "\n   🎬 FULLSCREEN FINALE 🎬" + "\n" + "="*40) # Shortened
    finale_stop_event.clear(); hInstance=GetModuleHandleW(None); className="FreakyFinaleWindowClass"
    wc=WNDCLASSEXW(); wc.cbSize=ctypes.sizeof(WNDCLASSEXW); wc.style=CS_HREDRAW|CS_VREDRAW
    wc.lpfnWndProc=finale_wnd_proc_instance; wc.hInstance=hInstance
    wc.hCursor=LoadCursorW(None,wintypes.LPCWSTR(IDC_ARROW)); wc.hbrBackground=wintypes.HBRUSH(COLOR_WINDOW+1)
    wc.lpszClassName=className; wc.hIcon=HICON(0); wc.hIconSm=HICON(0)
    if not RegisterClassExW(ctypes.byref(wc)): print(f"RegisterClassExW fail: {ctypes.get_last_error()}"); freaky_finale_direct_draw(width,height); return
    finale_window_hwnd=CreateWindowExW(0,className,"!!! SYS ALERT !!!",WS_POPUP|WS_VISIBLE,0,0,width,height,None,None,hInstance,None)
    if not finale_window_hwnd: print(f"CreateWindowExW fail: {ctypes.get_last_error()}"); freaky_finale_direct_draw(width,height); return
    SetWindowPos(finale_window_hwnd,HWND_TOPMOST,0,0,width,height,SWP_NOACTIVATE); ShowWindow(finale_window_hwnd,5); UpdateWindow(finale_window_hwnd)
    input_blocked = False
    if BlockInput(True): input_blocked=True # Don't print success/fail here, too noisy
    
    freaky_finale_on_window(finale_window_hwnd,width,height)

    if input_blocked: BlockInput(False) # Attempt unblock
    if finale_window_hwnd and IsWindow(finale_window_hwnd): DestroyWindow(finale_window_hwnd)
    finale_window_hwnd=None
    if not finale_stop_event.is_set():
        print("\nIssuing reboot..."); reboot_msg="System Maintenance Reboot" # Shorter message
        if not InitiateSystemShutdownExW(None,reboot_msg,5,True,True,SHTDN_REASON_MAJOR_OPERATINGSYSTEM|SHTDN_REASON_MINOR_RECONFIG|SHTDN_REASON_FLAG_PLANNED): print(f"Reboot fail: {ctypes.get_last_error()}")
        else: print("Reboot cmd OK.")
    else: print("Reboot cancelled.")
    time.sleep(2) # Very short final sleep

def freaky_finale_on_window(hwnd, width, height): # (Same as before, with its own message pump logic)
    global finale_stop_event
    hdc_finale=GetDC(hwnd)
    if not hdc_finale: return
    bg_c=RGB(0,0,100);txt_c=RGB(220,220,220);bg_b=CreateSolidBrush(bg_c);old_b=SelectObject(hdc_finale,bg_b)
    PatBlt(hdc_finale,0,0,width,height,PATCOPY);SetBkMode(hdc_finale,TRANSPARENT);SetTextColor(hdc_finale,txt_c)
    err_msgs = ["CRITICAL SYSTEM ERROR","CODE: 0xBADF00D - KERNEL MELTDOWN","",
        "WINDOWS IS COMPROMISED.","REBOOTING TO PREVENT DATA LOSS."] # Shorter messages
    y_p=height//3 # Higher start
    for msg in err_msgs: txt_w=len(msg)*10;x_p=max(20,(width-txt_w)//2);TextOutW(hdc_finale,x_p,y_p,msg,len(msg));y_p+=30
    reboot_base="REBOOTING IN: ";y_p+=40
    for i in range(3, 0, -1): # Very short countdown: 3 seconds
        if finale_stop_event.is_set(): break
        full_m=f"{reboot_base}{i:1}s...";x_p_c=max(20,(width-len(full_m)*10)//2) # Wider char est.
        PatBlt(hdc_finale,x_p_c-20,y_p,len(full_m)*10+40,40,PATCOPY);TextOutW(hdc_finale,x_p_c,y_p,full_m,len(full_m))
        sys.stdout.write(f"\rFinale countdown: {i:1}s ");sys.stdout.flush()
        start_pump=time.monotonic();msg_pump=MSG()
        while time.monotonic()-start_pump<1.0: # 1s pump
            if finale_stop_event.is_set():break
            if user32.PeekMessageW(ctypes.byref(msg_pump),hwnd,0,0,0x0001): # PM_REMOVE
                if msg_pump.message==WM_KEYDOWN and msg_pump.wParam==VK_ESCAPE: finale_stop_event.set();break
                TranslateMessage(ctypes.byref(msg_pump));DispatchMessageW(ctypes.byref(msg_pump))
            if finale_stop_event.is_set():break
            time.sleep(0.005)
        if finale_stop_event.is_set():break
    SelectObject(hdc_finale,old_b);DeleteObject(bg_b);ReleaseDC(hwnd,hdc_finale)

def freaky_finale_direct_draw(width, height): # Fallback (same as before, shorter countdown)
    print("\n" + "="*40 + "\n   🎬 FALLBACK FINALE 🎬" + "\n" + "="*40)
    finale_hdc=GetDC(None)
    if not finale_hdc: InitiateSystemShutdownExW(None,"Reboot",10,True,True,SHTDN_REASON_MAJOR_OPERATINGSYSTEM); return
    bg_c=RGB(0,0,100);txt_c=RGB(220,220,220);bg_b=CreateSolidBrush(bg_c);old_b=SelectObject(finale_hdc,bg_b)
    PatBlt(finale_hdc,0,0,width,height,PATCOPY);SetBkMode(finale_hdc,TRANSPARENT);SetTextColor(finale_hdc,txt_c)
    err_msgs=["CRITICAL SYSTEM ERROR","CODE: 0xBADF00D - KERNEL MELTDOWN","REBOOTING..."]
    y_p=height//3
    for msg in err_msgs: txt_w=len(msg)*10;x_p=max(20,(width-txt_w)//2);TextOutW(finale_hdc,x_p,y_p,msg,len(msg));y_p+=30
    reboot_base="REBOOTING IN: ";y_p+=40
    for i in range(3,0,-1):
        if bytebeat_stop_event.is_set(): break
        full_m=f"{reboot_base}{i:1}s...";x_p_c=max(20,(width-len(full_m)*10)//2)
        PatBlt(finale_hdc,x_p_c-20,y_p,len(full_m)*10+40,40,PATCOPY);TextOutW(finale_hdc,x_p_c,y_p,full_m,len(full_m))
        sys.stdout.write(f"\rFallback countdown: {i:1}s ");sys.stdout.flush();time.sleep(1)
    SelectObject(finale_hdc,old_b);DeleteObject(bg_b);ReleaseDC(None,finale_hdc)
    if not bytebeat_stop_event.is_set():
        if not InitiateSystemShutdownExW(None,"Rebooting",5,True,True,SHTDN_REASON_MAJOR_OPERATINGSYSTEM): print(f"Fallback Reboot fail: {ctypes.get_last_error()}")
        else: print("Fallback Reboot cmd OK.")
    else: print("Fallback Reboot cancelled.")
    time.sleep(2)

# --- Script Entry Point ---
if __name__ == "__main__":
    if sys.platform != "win32": print("Windows-only script."); sys.exit(1)
    try: COLORONCOLOR = gdi32.COLORONCOLOR
    except AttributeError: COLORONCOLOR = 3
    
    # Display brief, stern warning immediately.
    print("="*70)
    print("EXTREME WARNING: This script causes intense visual/audio effects and REBOOTS.")
    print("ONLY RUN IN A VM. YOU ARE RESPONSIBLE FOR ANY CONSEQUENCES.")
    print("Requires Administrator privileges - will attempt to elevate.")
    print("Audio can be LOUD. Lower volume NOW.")
    print("="*70)
    # No countdown here, admin check is next and might pause for UAC

    try:
        main()
    except KeyboardInterrupt: print("\nCtrl+C (global). Terminating.")
    except SystemExit as e: print(f"SystemExit: Script terminating ({e}).") # Usually from admin re-launch
    except Exception as e_global: print(f"\nGLOBAL ERROR: {e_global}"); import traceback; traceback.print_exc()
    finally:
        print("\n--- Finalizing Script ---")
        if bytebeat_thread_obj and bytebeat_thread_obj.is_alive():
            if not bytebeat_stop_event.is_set(): bytebeat_stop_event.set()
            bytebeat_thread_obj.join(1)
        PlaySoundA(None,None,SND_PURGE)
        BlockInput(False) # Crucial last-ditch effort to unblock input
        print("Script finished.")