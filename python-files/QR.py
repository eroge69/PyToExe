import tkinter as tk
from tkinter import ttk # For themed widgets like Entry, Button
from tkinter import messagebox
import threading
import time
import cv2
import numpy as np
from mss import mss, ScreenShotError # Import ScreenShotError for specific handling
from pyzbar import pyzbar
from PIL import Image, ImageTk # Pillow for Tkinter image display
import traceback # For printing full tracebacks

class QRCodeScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("手機鏡頭 QR Code 掃描器 (Scrcpy + 全螢幕擷取)") # Title changed
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing) # Handle window close

        # --- Variables ---
        # self.capture_region REMOVED - Not needed anymore
        self.scanning = False
        self.scan_thread = None
        self.sct = None # mss instance, initialized in the thread
        self.primary_monitor = None # Store primary monitor info
        self.last_decoded_data = None
        self.last_decode_time = 0
        self.debounce_time = 3 # seconds

        # --- GUI Setup ---
        # Frame for info (Replaces settings)
        info_frame = ttk.Frame(root, padding="10")
        info_frame.grid(row=0, column=0, sticky="ew")

        # REMOVED - Top, Left, Width, Height entries and labels

        ttk.Label(info_frame, text="將掃描整個主螢幕畫面。").pack() # Info label

        # Frame for video display
        video_frame = ttk.Frame(root, padding="10")
        video_frame.grid(row=1, column=0, sticky="nsew")
        self.video_label = ttk.Label(video_frame, text="影像預覽區域 (點擊 '開始掃描')")
        self.video_label.pack(expand=True, fill="both")
        self.photo_image = None

        # Frame for results and controls
        results_frame = ttk.Frame(root, padding="10")
        results_frame.grid(row=2, column=0, sticky="ew")

        ttk.Label(results_frame, text="掃描結果:").grid(row=0, column=0, sticky="w")
        self.result_text = tk.StringVar()
        self.result_entry = ttk.Entry(results_frame, textvariable=self.result_text, state='readonly', width=50)
        self.result_entry.grid(row=0, column=1, padx=5, sticky="ew")

        self.start_button = ttk.Button(results_frame, text="開始掃描 (全螢幕)", command=self.start_scan) # Button text changed
        self.start_button.grid(row=1, column=0, pady=10, padx=5)

        self.stop_button = ttk.Button(results_frame, text="停止掃描", command=self.stop_scan, state=tk.DISABLED)
        self.stop_button.grid(row=1, column=1, pady=10, padx=5)

        # Status Bar
        self.status_var = tk.StringVar()
        self.status_var.set("閒置 - 請先執行 scrcpy --video-source=camera") # Status text simplified
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding="2")
        status_bar.grid(row=3, column=0, sticky="ew")

        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(1, weight=1) # Let video frame expand
        results_frame.columnconfigure(1, weight=1) # Let result entry expand

    def update_status(self, message):
        self.status_var.set(message)

    def update_result(self, data):
        self.result_text.set(data)

    # update_video_display function remains the same as before

    def update_video_display(self, frame):
        try:
            # Check if frame is valid
            if frame is None or frame.size == 0:
                print("DEBUG: update_video_display received an invalid frame.")
                self.video_label.config(image=None, text="影像來源無效")
                return

            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)

            label_w = self.video_label.winfo_width()
            label_h = self.video_label.winfo_height()
            if label_w > 1 and label_h > 1:
                 # Downscale significantly for preview to improve performance
                 preview_w = min(label_w, 800) # Limit preview width
                 preview_h = int(preview_w * img_pil.height / img_pil.width)
                 if preview_h > label_h:
                      preview_h = label_h
                      preview_w = int(preview_h * img_pil.width / img_pil.height)

                 img_pil = img_pil.resize((preview_w, preview_h), Image.LANCZOS) # Use LANCZOS or ANTIALIAS


            self.photo_image = ImageTk.PhotoImage(image=img_pil)
            self.video_label.config(image=self.photo_image, text="")
        except Exception as e:
            print(f"無法更新影像畫面: {e}")
            self.video_label.config(image=None, text="影像顯示錯誤")

    def start_scan(self):
        if self.scanning:
            return

        # REMOVED - Reading capture region from GUI is no longer needed

        self.scanning = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.update_status("啟動掃描中... (掃描整個主螢幕)") # Status updated
        self.update_result("")
        self.last_decoded_data = None
        self.video_label.config(image=None, text="影像預覽區域 (掃描啟動中...)")

        # MSS Initialization moved to scan_loop thread

        self.scan_thread = threading.Thread(target=self.scan_loop, daemon=True)
        self.scan_thread.start()

    def stop_scan(self):
        # stop_scan function remains the same as before
        if not self.scanning:
            return
        print("stop_scan: Setting self.scanning to False")
        self.scanning = False
        self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))
        self.root.after(0, self.update_status, "閒置")


    def scan_loop(self):
        """This function runs in a separate thread."""
        print(f"[{time.time():.2f}] Scan Thread: Started.")
        last_frame_time = 0
        # **Increase frame delay slightly for full screen capture?**
        frame_delay = 0.1 # Approx 10 FPS - Adjust based on performance

        self.sct = None
        self.primary_monitor = None # Reset monitor info

        try:
            # == Initialize MSS here ==
            print(f"[{time.time():.2f}] Scan Thread: Initializing MSS within the thread...")
            self.sct = mss()
            print(f"[{time.time():.2f}] Scan Thread: MSS initialized successfully.")

            # == Get Primary Monitor Info ==
            if len(self.sct.monitors) < 2:
                 print(f"[{time.time():.2f}] Scan Thread: Error - Could not find primary monitor (monitor index 1). Monitors detected: {self.sct.monitors}")
                 raise RuntimeError("未找到主監視器資訊 (需要 monitor[1])")
            self.primary_monitor = self.sct.monitors[1]
            print(f"[{time.time():.2f}] Scan Thread: Using primary monitor: {self.primary_monitor}")
            self.root.after(0, self.update_status, f"掃描中... (整個主螢幕: {self.primary_monitor['width']}x{self.primary_monitor['height']})")

            while self.scanning:
                current_frame_time = time.time()
                # Frame rate limiting
                if current_frame_time - last_frame_time < frame_delay:
                     time.sleep(frame_delay - (current_frame_time - last_frame_time))
                last_frame_time = time.time()

                # --- Inner Try-Except ---
                try:
                    print(f"[{time.time():.2f}] Scan Loop: Iteration start.")

                    if self.sct is None or self.primary_monitor is None:
                        print(f"[{time.time():.2f}] Scan Loop: ERROR - self.sct or self.primary_monitor is None mid-loop!")
                        time.sleep(0.5)
                        continue

                    # == Capture screen (using primary_monitor) ==
                    print(f"[{time.time():.2f}] Scan Loop: About to call self.sct.grab(primary_monitor)")
                    sct_img = self.sct.grab(self.primary_monitor) # Capture primary monitor
                    print(f"[{time.time():.2f}] Scan Loop: Returned from self.sct.grab()")

                    # ... (Rest of the image processing, decoding, GUI updates remain the same) ...
                    # ... (Including conversion, preview update, pyzbar decode, debounce, etc.) ...
                    if sct_img is None:
                         print(f"[{time.time():.2f}] Scan Loop: self.sct.grab() returned None.")
                         time.sleep(0.1)
                         continue

                    print(f"[{time.time():.2f}] Scan Loop: About to call cv2.cvtColor()")
                    frame_bgr = cv2.cvtColor(np.array(sct_img), cv2.COLOR_BGRA2BGR)
                    print(f"[{time.time():.2f}] Scan Loop: Returned from cv2.cvtColor()")

                    if frame_bgr is None or frame_bgr.size == 0:
                         print(f"[{time.time():.2f}] Scan Loop: cvtColor resulted in invalid frame.")
                         continue

                    display_frame = frame_bgr.copy()
                    print(f"[{time.time():.2f}] Scan Loop: Scheduling update_video_display()")
                    self.root.after(0, lambda f=display_frame: self.update_video_display(f))

                    print(f"[{time.time():.2f}] Scan Loop: About to call pyzbar.decode()")
                    decoded_objects = pyzbar.decode(frame_bgr)
                    print(f"[{time.time():.2f}] Scan Loop: Returned from pyzbar.decode(). Found {len(decoded_objects)} objects.")

                    found_this_frame = False
                    current_time = time.time()
                    print(f"[{time.time():.2f}] Scan Loop: Entering loop for decoded objects (if any)")
                    for obj in decoded_objects:
                        print(f"[{time.time():.2f}] Scan Loop: Processing object")
                        try:
                           data = obj.data.decode('utf-8')
                           found_this_frame = True
                           if data != self.last_decoded_data or (current_time - self.last_decode_time > self.debounce_time):
                               print(f"[{time.time():.2f}] Scan Loop: QR Code Found (debounce passed): {data}")
                               self.last_decoded_data = data
                               self.last_decode_time = current_time
                               print(f"[{time.time():.2f}] Scan Loop: Scheduling update_result() and update_status()")
                               self.root.after(0, lambda d=data: self.update_result(d))
                               self.root.after(0, lambda t=time.strftime('%H:%M:%S'): self.update_status(f"找到 QR Code (上次更新於 {t})"))
                           break # Process only the first QR code
                        except UnicodeDecodeError:
                           print(f"[{time.time():.2f}] Scan Loop: Could not decode QR data as UTF-8.")
                        except Exception as decode_err:
                           print(f"[{time.time():.2f}] Scan Loop: Error processing decoded object: {decode_err}")

                    print(f"[{time.time():.2f}] Scan Loop: Exited loop for decoded objects")

                    if not found_this_frame and self.scanning:
                        print(f"[{time.time():.2f}] Scan Loop: Scheduling update_status() (scanning, no QR)")
                        # Status message doesn't need region anymore
                        self.root.after(0, lambda: self.update_status(f"掃描中... (整個主螢幕)"))

                    print(f"[{time.time():.2f}] Scan Loop: Reached end of inner try block successfully.")


                except ScreenShotError as sse:
                    print(f"[{time.time():.2f}] Scan Loop: *** INNER ScreenShotError CAUGHT! ***")
                    print(f"[{time.time():.2f}] Scan Loop: Error: {sse}")
                    traceback.print_exc()
                    print(f"擷取畫面失敗: {sse}")
                    self.root.after(0, lambda: messagebox.showerror("擷取錯誤", f"擷取主螢幕畫面時發生嚴重錯誤:\n{sse}\n\n掃描將停止。"))
                    self.root.after(0, self.stop_scan)
                    break # Exit the while loop

                except Exception as e_inner:
                    print(f"[{time.time():.2f}] Scan Loop: *** INNER EXCEPTION CAUGHT! ***")
                    # ... (rest of inner exception handling is the same) ...
                    print(f"[{time.time():.2f}] Scan Loop: Inner Exception Type: {type(e_inner)}")
                    print(f"[{time.time():.2f}] Scan Loop: Inner Exception Value: {e_inner}")
                    print(f"[{time.time():.2f}] Scan Loop: --- Inner Full Traceback START ---")
                    traceback.print_exc()
                    print(f"[{time.time():.2f}] Scan Loop: --- Inner Full Traceback END ---")
                    print(f"內部處理錯誤: {e_inner}")
                    self.root.after(0, lambda: self.update_status(f"掃描時發生錯誤: {e_inner}"))
                    if isinstance(e_inner, AttributeError):
                         print(f"[{time.time():.2f}] Scan Loop: Stopping scan due to inner AttributeError.")
                         self.root.after(0, lambda: messagebox.showerror("內部錯誤", f"掃描處理中發生錯誤:\n{e_inner}\n掃描將停止。"))
                         self.root.after(0, self.stop_scan)
                         break

        # ... (Outer exception handling and finally block remain the same) ...
        except Exception as e_outer:
             print(f"[{time.time():.2f}] Scan Thread: *** OUTER EXCEPTION CAUGHT! (MSS Init failed?) ***")
             print(f"[{time.time():.2f}] Scan Thread: Outer Exception Type: {type(e_outer)}")
             print(f"[{time.time():.2f}] Scan Thread: Outer Exception Value: {e_outer}")
             print(f"[{time.time():.2f}] Scan Thread: --- Outer Full Traceback START ---")
             traceback.print_exc()
             print(f"[{time.time():.2f}] Scan Thread: --- Outer Full Traceback END ---")
             self.root.after(0, messagebox.showerror, "初始化錯誤", f"無法初始化螢幕擷取模組:\n{e_outer}")
             self.root.after(0, self.stop_scan)

        finally:
            if self.sct:
                print(f"[{time.time():.2f}] Scan Thread: Closing MSS object.")
                self.sct.close()
            self.sct = None
            self.primary_monitor = None # Clear monitor info
            print(f"[{time.time():.2f}] Scan Thread: Exiting loop and cleanup done. self.scanning={self.scanning}")
            if self.scanning:
                 self.root.after(0, self.stop_scan)


    def on_closing(self):
        # on_closing function remains the same as before
        if self.scanning:
            if messagebox.askokcancel("退出?", "掃描正在進行中，確定要退出嗎？ (將會停止掃描)"):
                self.stop_scan()
                self.root.after(100, self.root.destroy)
            else:
                return
        else:
            self.root.destroy()


if __name__ == "__main__":
    # **Updated startup messages**
    print("手機鏡頭 QR Code 掃描器 (Scrcpy + 全螢幕擷取)")
    print("警告：掃描整個螢幕會比指定區域消耗更多 CPU 資源，可能導致延遲。")
    print("請先手動開啟 Scrcpy 相機視窗。例如執行：")
    print("scrcpy --video-source=camera --camera-facing=back --max-fps=20 -N")
    print("(建議使用 --max-fps 限制幀率, -N 關閉 scrcpy 的裝置控制)")
    print("-----------------------------------------------------")
    print("此程式將自動擷取您的'主螢幕'進行掃描。")
    print("-----------------------------------------------------")

    main_root = tk.Tk()
    app = QRCodeScannerApp(main_root)
    main_root.mainloop()

    print("GUI程式已結束。")