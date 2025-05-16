import cv2
import os
import numpy as np
from insightface.app import FaceAnalysis
import pyodbc
import uuid
import time  
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules('insightface')
unknown_dir = "C:\\UnknownFaces"  # مجلد لحفظ صور الأشخاص غير المعروفين
os.makedirs(unknown_dir, exist_ok=True)  # إنشاء المجلد إذا لم يكن موجودًا

# إعداد الاتصال بقاعدة البيانات
Connection = pyodbc.connect(
       "Driver={ODBC Driver 17 for SQL Server};"
       "SERVER=localhost;"  # إذا كنت تستخدم نسخة Express
       "DATABASE=StuProject;"
       "UID=sa;"
       "PWD=sa123456;"
)
print("Hussin"*50)
cursor = Connection.cursor()

# إعداد مكتبة InsightFace
app = FaceAnalysis(providers=['CPUExecutionProvider'])  # استخدام GPU
app.prepare(ctx_id=0)

# تحميل الوجوه المعروفة
known_faces = {}
known_dir = "C:\\ImagOfStu"

for filename in os.listdir(known_dir):
    path = os.path.join(known_dir, filename)
    img = cv2.imread(path)
    faces = app.get(img)
    if faces:
        name = os.path.splitext(filename)[0]
        known_faces[name] = faces[0].embedding  # أول وجه فقط

# فتح الكاميرا
cap = cv2.VideoCapture(0)

def get_best_match(face_embedding):
    min_dist = float('inf')
    best_name = "Unknown"
    for name, emb in known_faces.items():
        dist = np.linalg.norm(face_embedding - emb)
        
        if dist < min_dist:
            min_dist = dist
            best_name = name
    # إذا كانت المسافة أكبر من العتبة، اعتبر الوجه غير معروف
    threshold = 25  # يمكن تعديل العتبة بناءً على التجربة
    return best_name if min_dist < threshold else "Unknown"

def add_student_to_database(name):
    # التحقق من وجود الاسم مسبقًا
    cursor.execute("SELECT COUNT(*) FROM Attendance WHERE StuName = ?", (name,))
    count = cursor.fetchone()[0]
    
    if count == 0:
        # إذا لم يكن موجودًا، أضفه
        cursor.execute("INSERT INTO Attendance (StuName) VALUES (?)", (name,))
        Connection.commit()
   
def add_unknown_to_database(image_path):
    # إضافة مسار الصورة فقط إلى جدول UnknownAttendance
    cursor.execute("INSERT INTO UnknownAttendance (ImagePath) VALUES (?)", (image_path,))
    Connection.commit()

# قائمة لتتبع الأشخاص المكتشفين
detected_faces = {}

while True:
    ret, frame = cap.read()
    if not ret:
        break

    faces = app.get(frame)
    current_time = time.time()

    for face in faces:
        box = face.bbox.astype(int)
        name = get_best_match(face.embedding)

        # رسم الصندوق والاسم
        cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)
        cv2.putText(frame, name, (box[0], box[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

        # التحقق من ثبات الشخص المكتشف
        if name in detected_faces:
            # إذا كان نفس الشخص، تحقق من مرور ثلاث ثوانٍ
            if current_time - detected_faces[name] >= 3:
                if name != "Unknown":
                    # إضافة الطالب إلى قاعدة البيانات
                    add_student_to_database(name)
                else:
                    # توليد UUID للشخص غير المعروف
                    uuid_name = str(uuid.uuid4())
                    unknown_image_path = os.path.join(unknown_dir, f"{uuid_name}.jpg")
                    cv2.imwrite(unknown_image_path, frame)
                    add_unknown_to_database(unknown_image_path)
                # إزالة الشخص من القائمة بعد الإجراء
                del detected_faces[name]
        else:
            # إذا كان الشخص جديدًا، أضفه إلى القائمة مع الوقت الحالي
            detected_faces[name] = current_time

    cv2.imshow("Face Recognition", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
Connection.close()

