import os
import smtplib
from email.message import EmailMessage
from mimetypes import guess_type

# ==== Configuration ====
FOLDER_PATH = 'C:/ftp/rb5gif'  
SENDER_EMAIL = 'ssbvp1911@gmail.com'
SENDER_PASSWORD = 'xijnkimogmrkqkbc'
RECEIVER_EMAIL = 'cwcvsk@gmail.com'
SUBJECT = 'Radar Images'
BODY = 'Please Find Attached RADAR Images by SS'

# ==== Prepare Email ====
msg = EmailMessage()
msg['Subject'] = SUBJECT
msg['From'] = SENDER_EMAIL
msg['To'] = RECEIVER_EMAIL
msg.set_content(BODY)

# Attach all image files
for filename in os.listdir(FOLDER_PATH):
    file_path = os.path.join(FOLDER_PATH, filename)
    if os.path.isfile(file_path):
        mime_type, _ = guess_type(file_path)
        if mime_type and mime_type.startswith('image'):
            with open(file_path, 'rb') as img:
                file_data = img.read()
                msg.add_attachment(file_data,
                                   maintype='image',
                                   subtype=mime_type.split('/')[1],
                                   filename=filename)

# ==== Send Email ====
try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
        smtp.send_message(msg)
    print("Email sent successfully!")
except Exception as e:
    print(f"Failed to send email: {e}")
    input("Press enter to close program")
