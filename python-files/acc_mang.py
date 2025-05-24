import sys
import os
import sqlite3
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                              QFileDialog, QScrollArea, QFrame, QMessageBox,
                              QInputDialog, QDialog, QFormLayout, QGraphicsDropShadowEffect)
from PySide6.QtGui import QPixmap, QImage, QFont, QIcon, QColor, QClipboard, QAction
from PySide6.QtCore import Qt, QSize, QBuffer, QPropertyAnimation, QEasingCurve, QTimer, Signal, QPoint, Property

# Custom clickable label with copy functionality
class ClickableLabel(QLabel):
    clicked = Signal()
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        
    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

# Custom button with hover effect
class ModernButton(QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(40)
        self._color = "#3b82f6"
        self._hover_color = "#2563eb"
        self._text_color = "#ffffff"
        self.setCursor(Qt.PointingHandCursor)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._color};
                color: {self._text_color};
                border: none;
                border-radius: 8px;
                padding: 10px 15px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {self._hover_color};
            }}
            QPushButton:pressed {{
                background-color: {self._hover_color};
                padding-top: 12px;
                padding-bottom: 8px;
            }}
        """)

# Toast notification
class Toast(QWidget):
    def __init__(self, parent=None, message="", duration=2000):
        super().__init__(parent)
        self.parent = parent
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        self.label = QLabel(message)
        self.label.setStyleSheet("""
            color: white;
            font-size: 14px;
            font-weight: bold;
        """)
        layout.addWidget(self.label)
        
        self.setStyleSheet("""
            background-color: rgba(0, 0, 0, 0.7);
            border-radius: 10px;
        """)
        
        # Position at the bottom of the parent
        self.resize(self.sizeHint())
        
        # Animation
        self.opacity = 0.0
        self.animation = QPropertyAnimation(self, b"opacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Timer for auto-close
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.hide_animation)
        self.timer.setSingleShot(True)
        self.timer.start(duration)
        
    def show_toast(self):
        # Position at the bottom center of the parent
        parent_rect = self.parent.rect()
        self.move(
            parent_rect.center().x() - self.width() // 2,
            parent_rect.bottom() - self.height() - 20
        )
        self.show()
        self.animation.start()
        
    def hide_animation(self):
        hide_anim = QPropertyAnimation(self, b"opacity")
        hide_anim.setDuration(300)
        hide_anim.setStartValue(1.0)
        hide_anim.setEndValue(0.0)
        hide_anim.setEasingCurve(QEasingCurve.InCubic)
        hide_anim.finished.connect(self.close)
        hide_anim.start()
        
    def get_opacity(self):
        return self.opacity
        
    def set_opacity(self, opacity):
        self.opacity = opacity
        self.setWindowOpacity(opacity)
        
    opacity = Property(float, get_opacity, set_opacity)

class AccountDialog(QDialog):
    def __init__(self, tool_name, tool_image_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Add Account for {tool_name}")
        self.setMinimumWidth(450)
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border-radius: 10px;
            }
            QLabel {
                color: #1e293b;
            }
            QLineEdit {
                padding: 12px;
                border-radius: 8px;
                border: 1px solid #cbd5e1;
                background-color: #f8fafc;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #3b82f6;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Display tool image
        image_container = QFrame()
        image_container.setStyleSheet("""
            background-color: #f1f5f9;
            border-radius: 15px;
            padding: 10px;
        """)
        image_layout = QVBoxLayout(image_container)
        
        image_label = QLabel()
        image_label.setFixedSize(180, 180)
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setScaledContents(True)
        image_label.setStyleSheet("border-radius: 10px;")
        
        pixmap = QPixmap()
        pixmap.loadFromData(tool_image_data)
        image_label.setPixmap(pixmap)
        
        image_layout.addWidget(image_label, alignment=Qt.AlignCenter)
        
        # Tool name
        name_label = QLabel(tool_name)
        name_label.setFont(QFont("Arial", 16, QFont.Bold))
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("color: #0f172a; margin-top: 10px;")
        image_layout.addWidget(name_label)
        
        layout.addWidget(image_container)
        
        # Form for username and password
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignLeft)
        
        username_label = QLabel("Username/Email:")
        username_label.setFont(QFont("Arial", 12))
        
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Enter username or email")
        self.username_edit.setMinimumHeight(45)
        
        password_label = QLabel("Password:")
        password_label.setFont(QFont("Arial", 12))
        
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Enter password")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setMinimumHeight(45)
        
        form_layout.addRow(username_label, self.username_edit)
        form_layout.addRow(password_label, self.password_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        save_btn = ModernButton("Save Account")
        save_btn._color = "#3b82f6"
        save_btn._hover_color = "#2563eb"
        save_btn.clicked.connect(self.accept)
        
        cancel_btn = ModernButton("Cancel")
        cancel_btn._color = "#64748b"
        cancel_btn._hover_color = "#475569"
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def get_credentials(self):
        return self.username_edit.text(), self.password_edit.text()

class ToolCard(QFrame):
    def __init__(self, tool_id, name, image_data, parent=None):
        super().__init__(parent)
        self.tool_id = tool_id
        self.name = name
        self.image_data = image_data
        self.parent_widget = parent
        
        self.setFrameShape(QFrame.NoFrame)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                padding: 15px;
            }
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
        self.setup_ui()
        self.load_accounts()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)
        
        # Tool image
        image_container = QFrame()
        image_container.setFixedSize(120, 120)
        image_container.setStyleSheet("""
            background-color: #f1f5f9;
            border-radius: 15px;
        """)
        
        image_layout = QVBoxLayout(image_container)
        image_layout.setContentsMargins(5, 5, 5, 5)
        
        self.image_label = QLabel()
        self.image_label.setFixedSize(110, 110)
        self.image_label.setScaledContents(True)
        self.image_label.setStyleSheet("border-radius: 10px;")
        
        if self.image_data:
            pixmap = QPixmap()
            pixmap.loadFromData(self.image_data)
            self.image_label.setPixmap(pixmap)
        
        image_layout.addWidget(self.image_label, alignment=Qt.AlignCenter)
        layout.addWidget(image_container)
        
        # Tool info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(15)
        
        # Tool name
        name_label = QLabel(self.name)
        name_label.setFont(QFont("Arial", 16, QFont.Bold))
        name_label.setStyleSheet("color: #0f172a;")
        info_layout.addWidget(name_label)
        
        # Accounts container
        self.accounts_container = QWidget()
        self.accounts_layout = QVBoxLayout(self.accounts_container)
        self.accounts_layout.setContentsMargins(0, 0, 0, 0)
        self.accounts_layout.setSpacing(10)
        info_layout.addWidget(self.accounts_container)
        
        # Add account button
        add_account_btn = ModernButton("Add Account")
        add_account_btn._color = "#10b981"
        add_account_btn._hover_color = "#059669"
        add_account_btn.clicked.connect(self.add_account)
        info_layout.addWidget(add_account_btn)
        
        layout.addLayout(info_layout, 1)
        
        # Delete tool button
        delete_btn = ModernButton("Delete Tool")
        delete_btn._color = "#ef4444"
        delete_btn._hover_color = "#dc2626"
        delete_btn.clicked.connect(self.delete_tool)
        layout.addWidget(delete_btn)
    
    def load_accounts(self):
        # Clear existing accounts
        while self.accounts_layout.count():
            item = self.accounts_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Get accounts from database
        conn = sqlite3.connect('tool_accounts.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password FROM accounts WHERE tool_id = ?", (self.tool_id,))
        accounts = cursor.fetchall()
        conn.close()
        
        if accounts:
            accounts_label = QLabel(f"Accounts ({len(accounts)}):")
            accounts_label.setFont(QFont("Arial", 14, QFont.Bold))
            accounts_label.setStyleSheet("color: #334155;")
            self.accounts_layout.addWidget(accounts_label)
            
            for account_id, username, password in accounts:
                account_frame = QFrame()
                account_frame.setStyleSheet("""
                    QFrame {
                        background-color: #f8fafc;
                        border-radius: 10px;
                        padding: 10px;
                    }
                    QFrame:hover {
                        background-color: #f1f5f9;
                    }
                """)
                
                account_layout = QVBoxLayout(account_frame)
                account_layout.setContentsMargins(15, 10, 15, 10)
                account_layout.setSpacing(8)
                
                # Username with copy functionality
                username_layout = QHBoxLayout()
                username_layout.setSpacing(10)
                
                username_icon = QLabel("👤")
                username_icon.setFixedWidth(20)
                username_layout.addWidget(username_icon)
                
                username_label = ClickableLabel(f"{username}")
                username_label.setFont(QFont("Arial", 13))
                username_label.setStyleSheet("color: #334155;")
                username_label.clicked.connect(lambda checked=False, text=username: self.copy_to_clipboard(text, "Username"))
                username_layout.addWidget(username_label)
                
                copy_username_btn = QPushButton("Copy")
                copy_username_btn.setFixedWidth(60)
                copy_username_btn.setCursor(Qt.PointingHandCursor)
                copy_username_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e2e8f0;
                        border-radius: 5px;
                        padding: 5px;
                        color: #475569;
                    }
                    QPushButton:hover {
                        background-color: #cbd5e1;
                    }
                """)
                copy_username_btn.clicked.connect(lambda checked=False, text=username: self.copy_to_clipboard(text, "Username"))
                username_layout.addWidget(copy_username_btn)
                
                account_layout.addLayout(username_layout)
                
                # Password with copy and show/hide functionality
                password_layout = QHBoxLayout()
                password_layout.setSpacing(10)
                
                password_icon = QLabel("🔒")
                password_icon.setFixedWidth(20)
                password_layout.addWidget(password_icon)
                
                self.password_label = ClickableLabel(f"{'•' * len(password)}")
                self.password_label.setFont(QFont("Arial", 13))
                self.password_label.setStyleSheet("color: #334155;")
                self.password_label.clicked.connect(lambda checked=False, text=password: self.copy_to_clipboard(text, "Password"))
                password_layout.addWidget(self.password_label)
                
                copy_password_btn = QPushButton("Copy")
                copy_password_btn.setFixedWidth(60)
                copy_password_btn.setCursor(Qt.PointingHandCursor)
                copy_password_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e2e8f0;
                        border-radius: 5px;
                        padding: 5px;
                        color: #475569;
                    }
                    QPushButton:hover {
                        background-color: #cbd5e1;
                    }
                """)
                copy_password_btn.clicked.connect(lambda checked=False, text=password: self.copy_to_clipboard(text, "Password"))
                password_layout.addWidget(copy_password_btn)
                
                show_btn = QPushButton("Show")
                show_btn.setFixedWidth(60)
                show_btn.setCursor(Qt.PointingHandCursor)
                show_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e2e8f0;
                        border-radius: 5px;
                        padding: 5px;
                        color: #475569;
                    }
                    QPushButton:hover {
                        background-color: #cbd5e1;
                    }
                """)
                show_btn.clicked.connect(lambda checked=False, pwd=password, lbl=self.password_label: self.toggle_password(pwd, lbl))
                password_layout.addWidget(show_btn)
                
                delete_account_btn = QPushButton("×")
                delete_account_btn.setFixedWidth(30)
                delete_account_btn.setCursor(Qt.PointingHandCursor)
                delete_account_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #ef4444;
                        color: white;
                        border-radius: 5px;
                        font-weight: bold;
                        font-size: 16px;
                    }
                    QPushButton:hover {
                        background-color: #dc2626;
                    }
                """)
                delete_account_btn.clicked.connect(lambda checked=False, aid=account_id: self.delete_account(aid))
                password_layout.addWidget(delete_account_btn)
                
                account_layout.addLayout(password_layout)
                
                self.accounts_layout.addWidget(account_frame)
        else:
            no_accounts_label = QLabel("No accounts added yet.")
            no_accounts_label.setStyleSheet("color: #64748b; font-style: italic; padding: 10px;")
            self.accounts_layout.addWidget(no_accounts_label)
    
    def copy_to_clipboard(self, text, type_text):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        
        # Show toast notification
        toast = Toast(self.parent_widget, f"{type_text} copied to clipboard!", 2000)
        toast.show_toast()
    
    def toggle_password(self, password, label):
        if "•" in label.text():
            label.setText(f"{password}")
        else:
            label.setText(f"{'•' * len(password)}")
    
    def add_account(self):
        account_dialog = AccountDialog(self.name, self.image_data, self.parent_widget)
        if account_dialog.exec_() == QDialog.Accepted:
            username, password = account_dialog.get_credentials()
            
            if username:  # Only save if username is provided
                # Save to database
                conn = sqlite3.connect('tool_accounts.db')
                cursor = conn.cursor()
                cursor.execute("INSERT INTO accounts (tool_id, username, password) VALUES (?, ?, ?)", 
                            (self.tool_id, username, password))
                conn.commit()
                conn.close()
                
                # Refresh accounts
                self.load_accounts()
    
    def delete_account(self, account_id):
        reply = QMessageBox.question(self.parent_widget, "Delete Account", 
                                    "Are you sure you want to delete this account?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            conn = sqlite3.connect('tool_accounts.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
            conn.commit()
            conn.close()
            
            # Refresh accounts
            self.load_accounts()
    
    def delete_tool(self):
        reply = QMessageBox.question(self.parent_widget, "Delete Tool", 
                                    "Are you sure you want to delete this tool and all its accounts?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            conn = sqlite3.connect('tool_accounts.db')
            cursor = conn.cursor()
            # Delete accounts first (foreign key constraint)
            cursor.execute("DELETE FROM accounts WHERE tool_id = ?", (self.tool_id,))
            # Delete tool
            cursor.execute("DELETE FROM tools WHERE id = ?", (self.tool_id,))
            conn.commit()
            conn.close()
            
            # Signal parent to refresh
            self.parent_widget.load_tools()

class ToolAccountManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tool Account Manager")
        self.setMinimumSize(900, 700)
        
        # Initialize database
        self.init_database()
        
        # Setup UI
        self.setup_ui()
        
        # Load existing tools
        self.load_tools()
    
    def init_database(self):
        # Create database if it doesn't exist
        conn = sqlite3.connect('tool_accounts.db')
        cursor = conn.cursor()
        
        # Create table for tools and accounts
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tools (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            image BLOB
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY,
            tool_id INTEGER,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            FOREIGN KEY (tool_id) REFERENCES tools (id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def setup_ui(self):
        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8fafc;
            }
        """)
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)
        
        # Header
        header_container = QFrame()
        header_container.setStyleSheet("""
            QFrame {
                background-color: #3b82f6;
                border-radius: 15px;
            }
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect(header_container)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(59, 130, 246, 100))
        shadow.setOffset(0, 5)
        header_container.setGraphicsEffect(shadow)
        
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(30, 20, 30, 20)
        
        header = QLabel("Tool Account Manager")
        header.setFont(QFont("Arial", 22, QFont.Bold))
        header.setStyleSheet("color: white;")
        header_layout.addWidget(header)
        
        # Add new tool button
        add_tool_btn = ModernButton("Add New Tool")
        add_tool_btn._color = "#ffffff"
        add_tool_btn._hover_color = "#f1f5f9"
        add_tool_btn._text_color = "#3b82f6"
        add_tool_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #3b82f6;
                border: none;
                border-radius: 8px;
                padding: 10px 15px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
            }
        """)
        add_tool_btn.clicked.connect(self.add_new_tool)
        header_layout.addWidget(add_tool_btn)
        
        main_layout.addWidget(header_container)
        
        # Scroll area for tools
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f5f9;
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
        """)
        
        self.tools_container = QWidget()
        self.tools_layout = QVBoxLayout(self.tools_container)
        self.tools_layout.setContentsMargins(5, 5, 5, 5)
        self.tools_layout.setAlignment(Qt.AlignTop)
        self.tools_layout.setSpacing(20)
        
        scroll_area.setWidget(self.tools_container)
        main_layout.addWidget(scroll_area)
        
        self.setCentralWidget(main_widget)
    
    def add_new_tool(self):
        # Get tool name
        tool_name, ok = QInputDialog.getText(self, "Add New Tool", "Enter tool name:")
        if not ok or not tool_name:
            return
        
        # Select image
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Tool Image", "", "Image Files (*.png *.jpg *.jpeg)")
        if not file_path:
            return
        
        # Convert image to binary
        with open(file_path, 'rb') as file:
            image_data = file.read()
        
        # Show account dialog with the tool image
        account_dialog = AccountDialog(tool_name, image_data, self)
        if account_dialog.exec_() == QDialog.Accepted:
            username, password = account_dialog.get_credentials()
            
            # Save tool to database
            conn = sqlite3.connect('tool_accounts.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO tools (name, image) VALUES (?, ?)", (tool_name, image_data))
            conn.commit()
            
            # Get the ID of the newly inserted tool
            tool_id = cursor.lastrowid
            
            # Save account to database
            if username:  # Only save if username is provided
                cursor.execute("INSERT INTO accounts (tool_id, username, password) VALUES (?, ?, ?)", 
                            (tool_id, username, password))
                conn.commit()
            
            conn.close()
            
            # Refresh tool list
            self.load_tools()
            
            # Show success toast
            toast = Toast(self, f"Tool '{tool_name}' added successfully!", 2000)
            toast.show_toast()
    
    def load_tools(self):
        # Clear existing tools
        while self.tools_layout.count():
            item = self.tools_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Get all tools from database
        conn = sqlite3.connect('tool_accounts.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, image FROM tools")
        tools = cursor.fetchall()
        conn.close()
        
        if not tools:
            no_tools_container = QFrame()
            no_tools_container.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-radius: 15px;
                    padding: 40px;
                }
            """)
            
            # Add shadow effect
            shadow = QGraphicsDropShadowEffect(no_tools_container)
            shadow.setBlurRadius(20)
            shadow.setColor(QColor(0, 0, 0, 30))
            shadow.setOffset(0, 4)
            no_tools_container.setGraphicsEffect(shadow)
            
            no_tools_layout = QVBoxLayout(no_tools_container)
            
            no_tools_label = QLabel("No tools added yet")
            no_tools_label.setFont(QFont("Arial", 18, QFont.Bold))
            no_tools_label.setAlignment(Qt.AlignCenter)
            no_tools_label.setStyleSheet("color: #64748b;")
            no_tools_layout.addWidget(no_tools_label)
            
            instruction_label = QLabel("Click 'Add New Tool' to get started")
            instruction_label.setFont(QFont("Arial", 14))
            instruction_label.setAlignment(Qt.AlignCenter)
            instruction_label.setStyleSheet("color: #94a3b8;")
            no_tools_layout.addWidget(instruction_label)
            
            self.tools_layout.addWidget(no_tools_container)
            return
        
        # Add each tool to the layout
        for tool_id, name, image_data in tools:
            tool_card = ToolCard(tool_id, name, image_data, self)
            self.tools_layout.addWidget(tool_card)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application font
    font = QFont("Arial")
    app.setFont(font)
    
    window = ToolAccountManager()
    window.show()
    sys.exit(app.exec())