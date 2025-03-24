import re

# اسم ملف الإدخال
input_file = r"file.txt"  # تأكد أن الملف موجود

# اسم ملف الإخراج (اختياري)
output_file = "extracted_sessions.txt"

# قائمة لتخزين الـ Session IDs
session_ids = []

# قراءة الملف واستخراج القيم
with open(input_file, "r", encoding="utf-8") as file:
    for line in file:
        match = re.search(r"sessionid=([\w%:.-]+)", line, re.IGNORECASE)
        if match:
            session_ids.append(match.group(1))

# طباعة النتائج
print("Extracted Session IDs:")
for session in session_ids:
    print(session)

# حفظ القيم في ملف جديد
with open(output_file, "w", encoding="utf-8") as file:
    for session in session_ids:
        file.write(session + "\n")

print(f"✅ تم استخراج {len(session_ids)} Session IDs وحفظها في {output_file}")