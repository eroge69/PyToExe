import sys
import cv2
import platform
import numpy as np
import pandas as pd
from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class PaperQualityApp:
    def __init__(self, master):
        self.master = master
        master.title("🧪 Paper Quality Control - Red Spot Analyzer")
        master.geometry("1200x900")
        master.resizable(True, True)
        
        ctk.set_appearance_mode("System")  # Light, Dark, or System
        ctk.set_default_color_theme("blue")

        self.top_frame = ctk.CTkFrame(master)
        self.top_frame.pack(pady=10, fill=ctk.X)

        self.label = ctk.CTkLabel(self.top_frame, text="Welcome!")
        self.label.pack(side=ctk.LEFT, padx=10)

        self.upload_button = ctk.CTkButton(self.top_frame, text="Browse Image", command=self.open_image)
        self.upload_button.pack(side=ctk.LEFT, padx=5)
        
        self.undo_button = ctk.CTkButton(self.top_frame, text="Undo Last Point", command=self.undo_last_point)
        self.undo_button.pack(side=ctk.LEFT, padx=5)
        
        self.zoom_label = ctk.CTkLabel(self.top_frame, text="Zoom %")
        self.zoom_label.pack(side=ctk.LEFT, padx=(20, 5))

        self.zoom_scale = ctk.CTkSlider(self.top_frame, from_=10, to=200, orientation="horizontal",
                                        command=self.update_zoom, number_of_steps=190)
        self.zoom_scale.set(50)
        self.zoom_scale.pack(side=ctk.LEFT, padx=5)
        
        self.save_button = ctk.CTkButton(self.top_frame, text="Save Results", command=self.save_results, hover_color="green")
        self.save_button.pack(side=ctk.LEFT, padx=5)
        
        self.result_label = ctk.CTkLabel(master, text="", justify=ctk.LEFT)
        self.result_label.pack(pady=10)

        self.image_frame = ctk.CTkFrame(master)
        self.image_frame.pack(fill=ctk.BOTH, expand=True)

        self.canvas_container = ctk.CTkFrame(self.image_frame)
        self.canvas_container.pack(fill=ctk.BOTH, expand=True)

        self.canvas_img = None
        self.original_canvas = None
        self.segmented_canvas = None
        self.filename = None
        self.new_column = None
        self.suffix = None
        self.prefix = None
        self.dataframes = []
        
        self.roi_coords = None
        self.roi_points = []
        self.point_ids = []  # Track drawn canvas item IDs for undo
        self.scale_factor = 0.5
        
        
    def ask_continue_or_exit(self):
        response = messagebox.askyesno("Exit after save?", "Do you want to exit?")
        if response:
             sys.exit(0)
        
    def save_results(self):
        if not self.dataframes:
            return       
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], title="Save results as CSV")
        if file_path:
            # Concatenate all partial DataFrames
            all_df = pd.concat(self.dataframes, axis=1)
            result = all_df.T.groupby(level=0).sum(min_count=1).T
            result = result.fillna("NO MEASURE")
            print(result)
            result.to_csv(file_path, index=True)
            self.ask_continue_or_exit()
        else:
            pass        
    
    def undo_last_point(self):
        if not self.roi_points:
            return
        self.roi_points.pop()  # Remove last point
        # Delete the last one or two canvas elements (dot + line)
        for _ in range(2):
            if self.point_ids:
                try:
                    self.canvas_img.delete(self.point_ids.pop())
                except:
                    pass

    def open_image(self):
        if self.original_canvas:
            self.original_canvas.get_tk_widget().destroy()
            self.original_canvas = None
        if self.segmented_canvas:
            self.segmented_canvas.get_tk_widget().destroy()
            self.segmented_canvas = None
        if self.canvas_container:
            self.canvas_container.destroy()
        
        self.result_label.configure(text="")
        self.canvas_container = ctk.CTkFrame(self.image_frame)
        self.canvas_container.pack(fill=ctk.BOTH, expand=True)

        file_path = filedialog.askopenfilename(filetypes=[
                            ("Image Files", "*.png *.jpg *.jpeg *.bmp *.tiff"),
                            ("PNG Files", "*.png"),
                            ("JPEG Files", "*.jpg *.jpeg"),
                            ("All Files", "*.*")])
        if file_path:
            self.filename = Path(file_path).stem
            stopword = '-'
            #Suffix
            _, _, res = self.filename.partition(stopword)
            self.suffix = int(res)
            #Prefix
            i= self.filename.find(stopword)
            self.prefix = self.filename[:i]
            self.image = Image.open(file_path).convert('RGB')
            self.image_np = np.array(self.image)
            self.display_scaled_image()

    def update_zoom(self, value):
        self.scale_factor = float(value) / 100.0
        if hasattr(self, 'image'):
            self.display_scaled_image()

    def display_scaled_image(self):
        self.roi_points = []
        for widget in self.canvas_container.winfo_children():
            widget.destroy()

        display_width = int(self.image.width * self.scale_factor)
        display_height = int(self.image.height * self.scale_factor)
        self.resized_image = self.image.resize((display_width, display_height), Image.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(self.resized_image)

        canvas = ctk.CTkCanvas(self.canvas_container, width=display_width, height=display_height, bg="white",
                               scrollregion=(0, 0, display_width, display_height))
        canvas.create_image(0, 0, anchor='nw', image=self.tk_image)
        canvas.pack(fill=ctk.BOTH, expand=True)

        canvas.bind("<ButtonPress-1>", self.on_point_click)
        canvas.bind("<MouseWheel>", self.on_mouse_wheel)  
        canvas.bind("<Button-4>", self.on_mouse_wheel)     
        canvas.bind("<Button-5>", self.on_mouse_wheel)    
        canvas.bind("<ButtonPress-2>", self.on_middle_button_down)
        canvas.bind("<B2-Motion>", self.on_middle_button_drag)

        self.canvas_img = canvas

    def on_point_click(self, event):
        if len(self.roi_points) == 4:
            return

        x = self.canvas_img.canvasx(event.x)
        y = self.canvas_img.canvasy(event.y)
        self.roi_points.append((x, y))

        r = 3
        dot_id = self.canvas_img.create_oval(x - r, y - r, x + r, y + r, fill='green')
        self.point_ids.append(dot_id)

        if len(self.roi_points) > 1:
            x1, y1 = self.roi_points[-2]
            x2, y2 = self.roi_points[-1]
            line_id = self.canvas_img.create_line(x1, y1, x2, y2, fill='green', width=2)
            self.point_ids.append(line_id)

        if len(self.roi_points) == 4:
            x1, y1 = self.roi_points[-1]
            x0, y0 = self.roi_points[0]
            close_id = self.canvas_img.create_line(x1, y1, x0, y0, fill='green', width=2)
            self.point_ids.append(close_id)

            xs, ys = zip(*self.roi_points)
            x_min, x_max = int(min(xs) / self.scale_factor), int(max(xs) / self.scale_factor)
            y_min, y_max = int(min(ys) / self.scale_factor), int(max(ys) / self.scale_factor)
            self.roi_coords = (x_min, y_min, x_max, y_max)
            self.process_roi()

    def on_middle_button_down(self, event):
        self.canvas_img.scan_mark(event.x, event.y)

    def on_mouse_wheel(self, event):
        system = platform.system()
        if system == "Darwin":  
            delta = 1.1 if event.num == 4 else 0.9
        else:
            delta = 1.1 if event.delta > 0 else 0.9

        current = self.zoom_scale.get()
        new_value = min(max(int(current * delta), 10), 200)
        if new_value != current:
            self.zoom_scale.set(new_value)
            self.scale_factor = new_value / 100.0
            self.display_scaled_image()

    def on_middle_button_drag(self, event):
        self.canvas_img.scan_dragto(event.x, event.y, gain=1)

    def process_roi(self):
        #df = pd.DataFrame()
        if not self.roi_coords:
            return
        if self.canvas_container:
            self.canvas_container.destroy()

        x0, y0, x1, y1 = self.roi_coords
        roi = self.image_np[y0:y1, x0:x1]
        hsv = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)
        
        lower_red1 = np.array([0, 50, 50])
        upper_red1 = np.array([10, 255, 255])
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)

        lower_red2 = np.array([160, 50, 50])
        upper_red2 = np.array([179, 255, 255])
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

        lower_red3 = np.array([170, 25, 75])
        upper_red3 = np.array([179, 255, 255])
        mask3 = cv2.inRange(hsv, lower_red3, upper_red3)
        
        mask = cv2.bitwise_or(mask1, mask2)
        mask = cv2.bitwise_or(mask, mask3)
        """
        lower_red1 = np.array([0, 60, 120])
        upper_red1 = np.array([10, 150, 200])

        lower_red2 = np.array([170, 60, 120])
        upper_red2 = np.array([180, 150, 200])
                
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red1)
        mask = cv2.bitwise_or(mask1, mask2)
        """
        kernal = np.ones((2, 2), "uint8")
        red_mask = cv2.dilate(mask, kernal)
        red_mask = cv2.erode(red_mask, kernal)
        visual_mask = cv2.bitwise_and(roi, roi, mask=red_mask)

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        mask_clean = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel)

        total_pixels = mask_clean.shape[0] * mask_clean.shape[1]
        red_pixels = np.count_nonzero(mask_clean)
        red_ratio = (red_pixels / total_pixels) * 100
        
        # Append df to list of dataframes
        df = pd.DataFrame({self.prefix:[round(red_ratio, 2)]}, index=[f'Red_Spot_Perc_{self.suffix}min'])
        self.dataframes.append(df)    
        # Display results of that image
        result_text = f"\u2705 Red Spot Analysis:\n\nTotal Pixels: {total_pixels}\nRed Pixels: {red_pixels}\nRed Concentration: {red_ratio:.2f}%"
        self.result_label.configure(text=result_text)
        
        fig1, ax1 = plt.subplots()
        ax1.imshow(roi)
        ax1.set_title("Selected ROI")
        ax1.axis('off')
        self.original_canvas = FigureCanvasTkAgg(fig1, master=self.image_frame)
        self.original_canvas.get_tk_widget().pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)
        self.original_canvas.draw()

        fig2, ax2 = plt.subplots()
        ax2.imshow(visual_mask, cmap='gray')
        ax2.set_title("Red Spots Mask")
        ax2.axis('off')
        self.segmented_canvas = FigureCanvasTkAgg(fig2, master=self.image_frame)
        self.segmented_canvas.get_tk_widget().pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)
        self.segmented_canvas.draw()

if __name__ == "__main__":
    root = ctk.CTk()
    app = PaperQualityApp(root)
    def on_closing():
        try:
            root.after_cancel(root.after_id)  # Only if you've used after()
        except:
            pass  # Ignore if not defined
        try:
            plt.close('all')
            root.quit()
            root.destroy()
        except Exception as e:
            print(f"Shutdown error: {e}")
        
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
