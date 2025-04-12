
import imaplib
import email
import base64
import tkinter as tk
from tkinter import messagebox, scrolledtext

# Конфигурация
IMAP_SERVER = "imap-mail.outlook.com"
IMAP_PORT = 993

class MailDemoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Outlook OAuth2 Mail Reader")

        tk.Label(root, text="Email:").pack()
        self.email_entry = tk.Entry(root, width=50)
        self.email_entry.pack()

        tk.Label(root, text="Access Token (OAuth2):").pack()
        self.token_text = tk.Text(root, height=5, width=60)
        self.token_text.pack()

        tk.Button(root, text="Показать письма", command=self.fetch_emails).pack(pady=10)

        self.output = scrolledtext.ScrolledText(root, width=100, height=30)
        self.output.pack(pady=10)

    def fetch_emails(self):
        user_email = self.email_entry.get().strip()
        access_token = self.token_text.get("1.0", "end").strip()

        if not user_email or not access_token:
            messagebox.showerror("Ошибка", "Укажи email и access token")
            return

        try:
            auth_string = f"user={user_email}\1auth=Bearer {access_token}\1\1"
            auth_bytes = base64.b64encode(auth_string.encode("utf-8"))

            mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
            mail.debug = 0

            mail.authenticate("XOAUTH2", lambda x: auth_bytes)

            mail.select("INBOX")
            status, messages = mail.search(None, "ALL")

            self.output.delete("1.0", tk.END)

            for num in messages[0].split()[-10:]:  # последние 10 писем
                status, data = mail.fetch(num, "(RFC822)")
                msg = email.message_from_bytes(data[0][1])
                subject = msg.get("Subject", "Без темы")
                from_ = msg.get("From", "Без отправителя")
                self.output.insert(tk.END, f"От: {from_}
Тема: {subject}
{'-'*60}
")

            mail.logout()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = MailDemoApp(root)
    root.mainloop()
