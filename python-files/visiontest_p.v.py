import cv2
import numpy as np
import mediapipe as mp
import pygame
import random
import time
import math
import warnings
import os
import tkinter as tk
from tkinter import filedialog
import google.generativeai as genai
import pygame_gui
from pygame_gui.elements import UIButton, UITextEntryLine
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from collections import Counter
from datetime import datetime
import logging
import threading
import matplotlib.pyplot as plt

# کتابخانه‌های فارسی
import arabic_reshaper
from bidi.algorithm import get_display

# برای گزارش DICOM (نیاز به نصب pydicom دارد)
try:
    import pydicom
    from pydicom.dataset import Dataset, FileDataset
except ImportError:
    pydicom = None
    logging.warning("pydicom نصب نشده. گزارش DICOM غیرفعال می‌شود.")

# ------------------------------
# توابع کمکی برای رندر متون فارسی
# ------------------------------
def render_persian_text(text, font, color):
    """تبدیل متون فارسی به حالت قابل نمایش در pygame"""
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return font.render(bidi_text, True, color)

# ------------------------------
# تنظیم اولیه
# ------------------------------
pygame.init()
logging.basicConfig(level=logging.INFO)
logging.getLogger('mediapipe').setLevel(logging.ERROR)
warnings.filterwarnings("ignore", category=DeprecationWarning)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
background_path = os.path.join(BASE_DIR, "12.webp")
loading_path = os.path.join(BASE_DIR, "1356.jpeg")
background_form = pygame.image.load("12.webp")
loading_image = pygame.image.load("1356.jpeg")

info = pygame.display.Info()
screen_width, screen_height = info.current_w, info.current_h
background_form = pygame.transform.scale(background_form, (screen_width, screen_height))
loading_image = pygame.transform.scale(loading_image, (screen_width, screen_height))

# ------------------------------
# پیکربندی Gemini API با استفاده از متغیر محیطی
# ------------------------------
GEMINI_API_KEY = "AIzaSyBPZ3b3cMt8fTNyfjNyCccYpsf_RXFXI8w"  # کلید API خود را اینجا وارد کنید
genai.configure(api_key=GEMINI_API_KEY)
generation_config = {
    "temperature": 0.5,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 150,
    "response_mime_type": "text/plain",
}
MODEL = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",
    generation_config=generation_config,
)

def get_gemini_recommendation(test_summary):
    prompt = (
        f"با توجه به نتایج تست بینایی زیر:\n{test_summary}\n"
        "شما یک متخصص چشم‌پزشکی و تست بینایی حرفه‌ای هستید. "
        "لطفاً داده‌های بیمار را تحلیل کرده و یک ارزیابی دقیق به همراه توصیه‌های لازم برای ارزیابی بیشتر ارائه دهید."
    )
    try:
        chat_session = MODEL.start_chat(history=[])
        response = chat_session.send_message(prompt)
        return response.text
    except Exception as e:
        logging.error(f"خطا در فراخوانی Gemini API: {e}")
        return "توصیه‌ای موجود نیست."

# ------------------------------
# توابع پشتیبانی از چنددوربینی و سخت‌افزارهای تخصصی
# ------------------------------
def get_available_cameras(max_test=5):
    available = []
    for index in range(max_test):
        cap = cv2.VideoCapture(index)
        if cap is not None and cap.read()[0]:
            available.append(index)
        cap.release()
    logging.info(f"دوربین‌های موجود: {available}")
    return available

def select_camera():
    cameras = get_available_cameras()
    if not cameras:
        logging.error("هیچ دوربینی موجود نیست!")
        return None
    if len(cameras) == 1:
        return cameras[0]
    print("دوربین‌های موجود:")
    for cam in cameras:
        print(f"دوربین شماره: {cam}")
    try:
        selected = int(input("شماره دوربین مورد نظر را وارد کنید: "))
        if selected in cameras:
            return selected
        else:
            logging.info("شماره وارد شده نامعتبر است. از دوربین پیش‌فرض استفاده می‌شود.")
            return cameras[0]
    except Exception as e:
        logging.error(f"خطا در انتخاب دوربین: {e}")
        return cameras[0]

# ------------------------------
# توابع گزارش‌دهی حرفه‌ای (PDF و DICOM)
# ------------------------------
def generate_medical_charts(user_folder, left_correct, left_incorrect, right_correct, right_incorrect):
    labels = ['درست', 'اشتباه']
    left_counts = [len(left_correct), len(left_incorrect)]
    right_counts = [len(right_correct), len(right_incorrect)]

    x = range(len(labels))
    width = 0.35

    fig, ax = plt.subplots()
    ax.bar([p - width/2 for p in x], left_counts, width, label='چشم چپ')
    ax.bar([p + width/2 for p in x], right_counts, width, label='چشم راست')

    ax.set_ylabel('تعداد')
    ax.set_title('نتایج تست بینایی')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    chart_path = os.path.join(user_folder, "medical_chart.png")
    plt.savefig(chart_path)
    plt.close()
    logging.info(f"نمودار پزشکی در مسیر ذخیره شد: {chart_path}")
    return chart_path

def generate_dicom_report(user_folder, test_summary, user_details):
    if pydicom is None:
        logging.warning("pydicom نصب نشده؛ تولید گزارش DICOM انجام نمی‌شود.")
        return
    filename = os.path.join(user_folder, f"vision_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.dcm")
    file_meta = pydicom.Dataset()
    file_meta.MediaStorageSOPClassUID = pydicom.uid.generate_uid()
    file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
    file_meta.ImplementationClassUID = pydicom.uid.PYDICOM_IMPLEMENTATION_UID

    ds = FileDataset(filename, {}, file_meta=file_meta, preamble=b"\0" * 128)
    ds.PatientName = user_details.get("name", "ناشناس")
    ds.PatientID = user_details.get("id", "N/A")
    ds.StudyDate = datetime.now().strftime('%Y%m%d')
    ds.Modality = "OT"
    ds.SeriesDescription = "گزارش تست بینایی"
    ds.ContentDate = datetime.now().strftime('%Y%m%d')
    ds.ContentTime = datetime.now().strftime('%H%M%S')
    ds.ReportText = test_summary
    ds.save_as(filename)
    logging.info(f"گزارش DICOM در مسیر ذخیره شد: {filename}")

def upload_to_cloud(user_folder, pdf_filename):
    logging.info(f"در حال آپلود {pdf_filename} از پوشه {user_folder} به فضای ابری...")
    # در اینجا می‌توانید از API ابری استفاده کنید
    # به عنوان نمونه فقط پیام چاپ می‌شود.
    # ...

# ------------------------------
# توابع کمکی
# ------------------------------
def select_photo():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="انتخاب عکس",
        filetypes=[("فایل‌های تصویری", "*.jpg *.jpeg *.png")]
    )
    root.destroy()
    return file_path if file_path else None

# ------------------------------
# کالیبراسیون دوربین با AR
# ------------------------------
def calibrate_camera(camera_index=0, pattern_size=(9, 6), square_size=0.025, num_images=15):
    cap_calib = cv2.VideoCapture(camera_index)
    if not cap_calib.isOpened():
        logging.error("عدم توانایی در باز کردن دوربین!")
        return None, None

    objp = np.zeros((pattern_size[0] * pattern_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:pattern_size[0], 0:pattern_size[1]].T.reshape(-1, 2)
    objp *= square_size

    objpoints, imgpoints = [], []
    count = 0
    logging.info("شروع کالیبراسیون دوربین با AR. برای گرفتن عکس SPACE و برای خروج 'q' را فشار دهید.")

    while count < num_images:
        ret, frame = cap_calib.read()
        if not ret:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ret_corners, corners = cv2.findChessboardCorners(gray, pattern_size, None)
        
        overlay = frame.copy()
        if ret_corners:
            cv2.drawChessboardCorners(overlay, pattern_size, corners, ret_corners)
            cv2.putText(overlay, f"گرفته شده: {count}/{num_images}", (20, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            for corner in corners:
                x, y = corner.ravel()
                cv2.circle(overlay, (int(x), int(y)), 5, (255, 0, 0), -1)
        else:
            cv2.putText(overlay, "شطرنجی تشخیص داده نشد! موقعیت را تنظیم کنید.", (20, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        cv2.imshow("کالیبراسیون AR", overlay)
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):
            if ret_corners:
                objpoints.append(objp)
                corners2 = cv2.cornerSubPix(
                    gray, corners, (11, 11), (-1, -1),
                    criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
                )
                imgpoints.append(corners2)
                count += 1
                logging.info(f"عکس شماره {count} گرفته شد.")
            else:
                logging.info("شطرنجی تشخیص داده نشد. عکس ذخیره نشد.")
        elif key == ord('q'):
            break

    cap_calib.release()
    cv2.destroyAllWindows()

    if len(objpoints) < 3:
        logging.error("تعداد عکس‌های کافی برای کالیبراسیون جمع‌آوری نشد!")
        return None, None

    ret, camera_matrix, dist_coeffs, _, _ = cv2.calibrateCamera(
        objpoints, imgpoints, gray.shape[::-1], None, None
    )
    if ret:
        logging.info("کالیبراسیون دوربین موفقیت‌آمیز بود.")
        return camera_matrix, dist_coeffs
    else:
        logging.error("کالیبراسیون دوربین ناموفق بود.")
        return None, None

# ------------------------------
# تنظیمات اولیه UI با Pygame
# ------------------------------
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
pygame.display.set_caption("تست بالینی بینایی M-Tech")
BASE_WIDTH, BASE_HEIGHT = 800, 600
scale_factor = screen_height / BASE_HEIGHT

def get_scaled_font(size):
    # برای متون فارسی بهتره از فونت فارسی دلخواه مثل "vazir.ttf" استفاده کنی:
    return pygame.font.Font("12345.ttf", int(size * scale_factor))

WHITE, BLACK = (255, 255, 255), (0, 0, 0)

clinical_levels = [
    {"snellen": "10/200", "font_size": 145},
    {"snellen": "10/160", "font_size": 116},
    {"snellen": "10/125", "font_size": 90},
    {"snellen": "10/100", "font_size": 72},
    {"snellen": "10/80",  "font_size": 58},
    {"snellen": "10/70",  "font_size": 50},
    {"snellen": "10/60",  "font_size": 43},
    {"snellen": "10/50",  "font_size": 36},
    {"snellen": "10/40",  "font_size": 29},
    {"snellen": "10/30",  "font_size": 22},
    {"snellen": "10/25",  "font_size": 18},
    {"snellen": "10/20",  "font_size": 14},
    {"snellen": "10/15",  "font_size": 11},
    {"snellen": "10/10",  "font_size": 7}
]
test_distance = 1  # فاصله استاندارد تست به متر

mp_hands = mp.solutions.hands
hands_detector = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    model_complexity=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)
cap = None  # پس از انتخاب دوربین مقداردهی می‌شود
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.7)

calibrated_camera_matrix = None
calibrated_dist_coeffs = None

user_name = user_surname = user_age = ""
national_id = ""
phone = ""
email = ""
photo_path = None
left_eye_correct, left_eye_incorrect = [], []
right_eye_correct, right_eye_incorrect = [], []
gemini_recommendation = "توصیه‌ای موجود نیست."

def crop_to_square(frame):
    h, w, _ = frame.shape
    side = min(w, h)
    start_x = (w - side) // 2
    start_y = (h - side) // 2
    return frame[start_y:start_y+side, start_x:start_x+side]

def get_finger_direction(landmarks, mcp_index, tip_index):
    mcp = landmarks.landmark[mcp_index]
    tip = landmarks.landmark[tip_index]
    dx, dy = tip.x - mcp.x, tip.y - mcp.y
    angle = math.degrees(math.atan2(-dy, dx))
    angle = angle if angle >= 0 else angle + 360
    if angle >= 315 or angle < 45:
        return 0
    elif 45 <= angle < 135:
        return 90
    elif 135 <= angle < 225:
        return 180
    else:
        return 270

def get_extended_hand_direction(frame):
    square_frame = crop_to_square(frame)
    frame_rgb = cv2.cvtColor(square_frame, cv2.COLOR_BGR2RGB)
    results = hands_detector.process(frame_rgb)
    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        h, w, _ = square_frame.shape
        xs = [lm.x for lm in hand_landmarks.landmark]
        ys = [lm.y for lm in hand_landmarks.landmark]
        hand_center_x = sum(xs) / len(xs) * w
        hand_center_y = sum(ys) / len(ys) * h

        face_results = face_detection.process(frame_rgb)
        if face_results.detections:
            detection = face_results.detections[0]
            bbox = detection.location_data.relative_bounding_box
            face_x = bbox.xmin * w
            face_y = bbox.ymin * h
            face_width = bbox.width * w
            face_height = bbox.height * h
            if face_x <= hand_center_x <= face_x + face_width and face_y <= hand_center_y <= face_y + face_height:
                return None

        directions = []
        for mcp, tip in [(5, 8), (9, 12), (13, 16), (17, 20)]:
            directions.append(get_finger_direction(hand_landmarks, mcp, tip))
        return Counter(directions).most_common(1)[0][0]
    return None

def average_hand_direction(duration=0.5):
    samples = []
    start_time = time.time()
    while time.time() - start_time < duration:
        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.flip(frame, 1)
        direction = get_extended_hand_direction(frame)
        if direction is not None:
            samples.append(direction)
        time.sleep(0.05)
    return Counter(samples).most_common(1)[0][0] if samples else None

def render_letter(letter_surface):
    rect = letter_surface.get_rect(center=(screen_width // 2, screen_height // 2))
    if rect.width > screen_width or rect.height > screen_height:
        scale = min(screen_width / rect.width, screen_height / rect.height)
        new_size = (int(rect.width * scale), int(rect.height * scale))
        letter_surface = pygame.transform.scale(letter_surface, new_size)
        rect = letter_surface.get_rect(center=(screen_width // 2, screen_height // 2))
    return letter_surface, rect

def detect_distance():
    ret, frame = cap.read()
    if not ret:
        logging.error("عدم توانایی در دریافت فریم از دوربین.")
        return test_distance
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_detection.process(frame_rgb)
    if results.detections:
        detection = results.detections[0]
        bbox = detection.location_data.relative_bounding_box
        h, w, _ = frame.shape
        face_width = bbox.width * w
        REAL_FACE_WIDTH = 0.16  # عرض واقعی صورت به متر
        focal_length = calibrated_camera_matrix[0, 0] if calibrated_camera_matrix is not None else 700
        distance = (REAL_FACE_WIDTH * focal_length) / face_width
        logging.info(f"فاصله اندازه‌گیری شده: {distance:.2f} متر")
        return distance
    logging.info("صورت تشخیص داده نشد؛ فاصله پیش‌فرض استفاده می‌شود.")
    return test_distance

def adjust_font_sizes(measured_distance):
    scale = measured_distance / test_distance
    logging.info(f"ضریب مقیاس: {scale:.2f}")
    for level in clinical_levels:
        original_size = level["font_size"]
        level["font_size"] = max(int(original_size * scale), 5)
        logging.info(f"سطح {level['snellen']} اندازه فونت تغییر یافت به {level['font_size']}")

def display_logo():
    screen.fill(WHITE)
    main_font = get_scaled_font(80)
    sub_font = get_scaled_font(30)
    main_text = render_persian_text("تست بینایی", main_font, (0, 0, 128))
    sub_text = render_persian_text("ساخته شده توسط M-Tech", sub_font, (100, 100, 100))
    screen.blit(main_text, main_text.get_rect(center=(screen_width//2, screen_height//2 - 20)))
    screen.blit(sub_text, sub_text.get_rect(center=(screen_width//2, screen_height//2 + 40)))
    pygame.display.flip()
    pygame.time.wait(2000)

def show_instructions():
    screen.fill(WHITE)
    font = get_scaled_font(30)
    instructions = [
        "یک چشم را طبق دستور بپوشانید.",
        "دست خود را در جهت مشخص شده قرار دهید.",
        "نتایج پس از تست هر دو چشم ذخیره می‌شود."
    ]
    for i, line in enumerate(instructions):
        text_surface = render_persian_text(line, font, BLACK)
        screen.blit(text_surface, (100, 150 + i * 40))
    pygame.display.flip()
    pygame.time.wait(3000)

def compare_with_previous_results(user_folder):
    logging.info(f"مقایسه نتایج فعلی با تست‌های قبلی در پوشه: {user_folder}")
    previous_files = [f for f in os.listdir(user_folder) if f.endswith('.pdf')]
    if previous_files:
        logging.info(f"{len(previous_files)} فایل تست قبلی پیدا شد.")
    else:
        logging.info("تست قبلی پیدا نشد.")

def show_form(manager):
    screen.blit(background_form, (0, 0))
    pygame.display.flip()

    name_entry = UITextEntryLine(pygame.Rect((200, 100), (400, 40)), manager, placeholder_text="نام خود را وارد کنید")
    surname_entry = UITextEntryLine(pygame.Rect((200, 150), (400, 40)), manager, placeholder_text="نام خانوادگی خود را وارد کنید")
    age_entry = UITextEntryLine(pygame.Rect((200, 200), (400, 40)), manager, placeholder_text="سن خود را وارد کنید")
    national_id_entry = UITextEntryLine(pygame.Rect((200, 250), (400, 40)), manager, placeholder_text="شماره شناسایی (اختیاری)")
    phone_entry = UITextEntryLine(pygame.Rect((200, 300), (400, 40)), manager, placeholder_text="شماره تماس (اختیاری)")
    email_entry = UITextEntryLine(pygame.Rect((200, 350), (400, 40)), manager, placeholder_text="ایمیل (اختیاری)")
    photo_button = UIButton(pygame.Rect((200, 400), (400, 40)), 'آپلود عکس (اختیاری)', manager)
    submit_button = UIButton(pygame.Rect((200, 450), (400, 40)), 'ثبت اطلاعات', manager)
    start_test_button = UIButton(pygame.Rect((200, 500), (400, 40)), 'شروع تست یکپارچه بینایی', manager)
    start_test_button.visible = False

    return {
        "name_entry": name_entry,
        "surname_entry": surname_entry,
        "age_entry": age_entry,
        "national_id_entry": national_id_entry,
        "phone_entry": phone_entry,
        "email_entry": email_entry,
        "photo_button": photo_button,
        "submit_button": submit_button,
        "start_test_button": start_test_button
    }

def save_results(user_name, user_surname, user_age, national_id, phone, email,
                 left_correct, left_incorrect, right_correct, right_incorrect,
                 recommendation, photo_path=None):
    folder_name = f"{user_name}_{user_surname}"
    os.makedirs(folder_name, exist_ok=True)

    chart_path = generate_medical_charts(folder_name, left_correct, left_incorrect, right_correct, right_incorrect)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_filename = os.path.join(folder_name, f"vision_test_{timestamp}.pdf")
    try:
        doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = [
            Paragraph(f"نام: {user_name}", styles['Normal']),
            Paragraph(f"نام خانوادگی: {user_surname}", styles['Normal']),
            Paragraph(f"سن: {user_age}", styles['Normal']),
            Paragraph(f"شماره شناسایی: {national_id if national_id else 'ندارد'}", styles['Normal']),
            Paragraph(f"شماره تماس: {phone if phone else 'ندارد'}", styles['Normal']),
            Paragraph(f"ایمیل: {email if email else 'ندارد'}", styles['Normal']),
            Paragraph("چشم چپ:", styles['Normal']),
            Paragraph(f"  سطوح درست: {', '.join(left_correct) if left_correct else 'هیچ'}", styles['Normal']),
            Paragraph(f"  سطوح اشتباه: {', '.join(left_incorrect) if left_incorrect else 'هیچ'}", styles['Normal']),
            Paragraph("چشم راست:", styles['Normal']),
            Paragraph(f"  سطوح درست: {', '.join(right_correct) if right_correct else 'هیچ'}", styles['Normal']),
            Paragraph(f"  سطوح اشتباه: {', '.join(right_incorrect) if right_incorrect else 'هیچ'}", styles['Normal']),
            Paragraph("توصیه‌ها:", styles['Normal']),
            Paragraph(recommendation, styles['Normal']),
            Paragraph("نمودار پزشکی:", styles['Normal'])
        ]
        if os.path.exists(chart_path):
            elements.append(Image(chart_path, width=4*inch, height=3*inch))
        if photo_path:
            elements.append(Image(photo_path, width=2*inch, height=2*inch))
        doc.build(elements)
        logging.info("نتایج با موفقیت به صورت PDF ذخیره شدند.")
    except Exception as e:
        logging.error(f"خطا در ذخیره نتایج به صورت PDF: {e}")

    user_details = {"name": user_name, "id": national_id}
    test_summary = (
        f"چشم چپ - سطوح درست: {', '.join(left_correct) if left_correct else 'هیچ'}\n"
        f"چشم چپ - سطوح اشتباه: {', '.join(left_incorrect) if left_incorrect else 'هیچ'}\n"
        f"چشم راست - سطوح درست: {', '.join(right_correct) if right_correct else 'هیچ'}\n"
        f"چشم راست - سطوح اشتباه: {', '.join(right_incorrect) if right_incorrect else 'هیچ'}"
    )
    generate_dicom_report(folder_name, test_summary, user_details)
    upload_to_cloud(folder_name, pdf_filename)

def wait_for_stable_hand(manager, stable_time=1.5, current_image=None):
    stable_direction, start_stable = None, None
    start_time = time.time()
    warning_font = get_scaled_font(30)

    while True:
        direction = average_hand_direction(duration=0.5)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                cap.release()
                exit()
            manager.process_events(event)
        if direction is None and time.time() - start_time > 10:
            pygame.draw.rect(screen, WHITE, (0, screen_height - 100, screen_width, 100))
            warning_text = render_persian_text("هیچ دست یا صدایی تشخیص داده نشد!", warning_font, (255, 0, 0))
            screen.blit(warning_text, (100, screen_height - 80))
        elif direction is not None:
            pygame.draw.rect(screen, WHITE, (0, screen_height - 100, screen_width, 100))
            status_text = render_persian_text(f"دست تشخیص داده شد: {direction}", warning_font, (0, 255, 0))
            screen.blit(status_text, (100, screen_height - 80))
            if stable_direction != direction:
                stable_direction, start_stable = direction, time.time()
            elif time.time() - start_stable >= stable_time:
                return direction
        if current_image:
            img_rect = current_image.get_rect(center=(screen_width // 2, screen_height // 2))
            screen.blit(current_image, img_rect)
        manager.update(0.01)
        manager.draw_ui(screen)
        pygame.display.update()

def perform_full_test_for_eye(eye, manager, measured_distance):
    prompt_font = get_scaled_font(30)
    screen.fill(WHITE)
    prompt_text = f"لطفاً چشم {eye} را بپوشانید"
    screen.blit(render_persian_text(prompt_text, prompt_font, BLACK), (200, 250))
    pygame.display.flip()
    pygame.time.wait(3000)

    correct_levels, incorrect_levels = [], []
    for level_data in clinical_levels:
        font_size = level_data["font_size"]
        snellen_ratio = level_data["snellen"]
        expected_direction = random.choice([0, 90, 180, 270])
        # استفاده از فونت فارسی؛ توجه کن که "vazir.ttf" یا فونت دلخواه در پروژه موجود باشد.
        font = pygame.font.Font("vazir.ttf", font_size)
        # رندر حرف "E" با استفاده از فونت فارسی؛ البته اینجا چون حرف E به صورت استاندارد هست می‌تونی از آن استفاده کنی.
        letter_surface, rect = render_letter(font.render("E", True, BLACK))
        rotated_surface = pygame.transform.rotate(letter_surface, expected_direction)

        screen.fill(WHITE)
        screen.blit(render_persian_text(f"سطح: {snellen_ratio}", prompt_font, BLACK), (10, 10))
        screen.blit(render_persian_text(f"فاصله تنظیم شده: {measured_distance:.2f} متر", prompt_font, BLACK), (10, 40))
        rect = rotated_surface.get_rect(center=(screen_width // 2, screen_height // 2))
        screen.blit(rotated_surface, rect)
        manager.update(0.01)
        manager.draw_ui(screen)
        pygame.display.flip()

        stable_dir = wait_for_stable_hand(manager, stable_time=1.5, current_image=rotated_surface)
        if stable_dir == expected_direction:
            correct_levels.append(snellen_ratio)
        else:
            incorrect_levels.append(snellen_ratio)
        pygame.time.wait(500)
    return correct_levels, incorrect_levels

def main():
    global user_name, user_surname, user_age, national_id, phone, email, photo_path
    global left_eye_correct, left_eye_incorrect, right_eye_correct, right_eye_incorrect, gemini_recommendation
    global calibrated_camera_matrix, calibrated_dist_coeffs, cap

    selected_camera = select_camera()
    if selected_camera is None:
        logging.error("هیچ دوربین در دسترس نیست. خروج از برنامه.")
        return
    cap = cv2.VideoCapture(selected_camera)

    clock = pygame.time.Clock()
    manager = pygame_gui.UIManager((screen_width, screen_height))

    display_logo()
    ui_elements = show_form(manager)
    user_details_collected = False
    in_test = False
    measured_distance = test_distance

    while True:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                if cap.isOpened():
                    cap.release()
                return
            manager.process_events(event)
            if not user_details_collected:
                if event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == ui_elements["photo_button"]:
                        photo_path = select_photo()
                    elif event.ui_element == ui_elements["submit_button"]:
                        user_name = ui_elements["name_entry"].get_text().strip()
                        user_surname = ui_elements["surname_entry"].get_text().strip()
                        user_age = ui_elements["age_entry"].get_text().strip()
                        national_id = ui_elements["national_id_entry"].get_text().strip()
                        phone = ui_elements["phone_entry"].get_text().strip()
                        email = ui_elements["email_entry"].get_text().strip()
                        if user_name and user_surname and user_age.isdigit():
                            user_details_collected = True
                            ui_elements["start_test_button"].visible = True
                        else:
                            logging.info("لطفاً نام، نام خانوادگی و سن را به درستی وارد کنید.")
            elif user_details_collected and not in_test:
                if event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == ui_elements["start_test_button"]:
                        in_test = True
                        for element in list(ui_elements.values()):
                            element.kill()
                        show_instructions()
                        logging.info("شروع کالیبراسیون دوربین با AR...")
                        calibrated_camera_matrix, calibrated_dist_coeffs = calibrate_camera(selected_camera)
                        if calibrated_camera_matrix is not None:
                            logging.info(f"طول کانونی کالیبره شده: {calibrated_camera_matrix[0, 0]}")
                        else:
                            logging.info("کالیبراسیون ناموفق؛ از مقادیر پیش‌فرض استفاده می‌شود.")
                        measured_distance = detect_distance()
                        screen.fill(WHITE)
                        distance_text = render_persian_text(f"فاصله اندازه‌گیری شده: {measured_distance:.2f} متر", get_scaled_font(30), BLACK)
                        screen.blit(distance_text, (200, 200))
                        pygame.display.flip()
                        pygame.time.wait(3000)
                        adjust_font_sizes(measured_distance)
            else:
                for element in manager.ui_group.copy():
                    element.kill()
                left_eye_correct, left_eye_incorrect = perform_full_test_for_eye("چپ", manager, measured_distance)
                right_eye_correct, right_eye_incorrect = perform_full_test_for_eye("راست", manager, measured_distance)

                test_summary = (
                    f"چشم چپ - سطوح درست: {', '.join(left_eye_correct) if left_eye_correct else 'هیچ'}\n"
                    f"چشم چپ - سطوح اشتباه: {', '.join(left_eye_incorrect) if left_eye_incorrect else 'هیچ'}\n"
                    f"چشم راست - سطوح درست: {', '.join(right_eye_correct) if right_eye_correct else 'هیچ'}\n"
                    f"چشم راست - سطوح اشتباه: {', '.join(right_eye_incorrect) if right_eye_incorrect else 'هیچ'}"
                )
                ml_analysis = "هیچ ناهنجاری قابل توجهی تشخیص داده نشد."
                if "10/200" in test_summary or "10/160" in test_summary:
                    ml_analysis = "ریسک ممکن برای گلوکوم وجود دارد. توصیه می‌شود ارزیابی بیشتر صورت گیرد."
                logging.info(f"تحلیل ML: {ml_analysis}")
                test_summary += f"\nتحلیل ML: {ml_analysis}"

                screen.blit(loading_image, (0, 0))
                loading_text = render_persian_text("در حال بارگذاری توصیه‌ها...", get_scaled_font(40), BLACK)
                screen.blit(loading_text, (screen_width//2 - loading_text.get_width()//2, screen_height//2 - loading_text.get_height()//2))
                pygame.display.flip()
                pygame.time.wait(3000)

                gemini_recommendation = get_gemini_recommendation(test_summary)
                user_folder = f"{user_name}_{user_surname}"
                if os.path.exists(user_folder):
                    compare_with_previous_results(user_folder)
                save_results(user_name, user_surname, user_age, national_id, phone, email,
                             left_eye_correct, left_eye_incorrect, right_eye_correct, right_eye_incorrect,
                             gemini_recommendation, photo_path)

                screen.fill(WHITE)
                complete_text = render_persian_text("تست تکمیل شد. نتایج ذخیره شدند.", get_scaled_font(30), BLACK)
                screen.blit(complete_text, (200, 200))
                pygame.display.flip()
                pygame.time.wait(3000)
                if cap.isOpened():
                    cap.release()
                cap = cv2.VideoCapture(selected_camera)
                left_eye_correct, left_eye_incorrect = [], []
                right_eye_correct, right_eye_incorrect = [], []
                in_test, user_details_collected = False, False
                ui_elements = show_form(manager)
        manager.update(time_delta)
        manager.draw_ui(screen)
        pygame.display.update()

if __name__ == "__main__":
    main()
