import sys
import secrets
import math
import json
import csv
import os
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QGroupBox, QLabel, QLineEdit, QPushButton, QCheckBox, QSlider,
                             QListWidget, QProgressBar, QMessageBox, QToolTip,
                             QTabWidget, QFileDialog, QInputDialog, QDialog, QListWidgetItem)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QClipboard, QFont, QPalette, QColor

# Suppress Qt platform theme warnings
os.environ["QT_LOGGING_RULES"] = "*.debug=false"

# Configuration
CONFIG_FILE = "config.json"
SAVED_PASSWORDS_FILE = "saved_passwords.json"
WORDLIST_FILE = "wordlist.txt"

class PasswordGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔒 PassCraft (Ulimate Password Generator) - By SABIR")
        self.setGeometry(100, 100, 900, 700)
        self.saved_passwords = []
        self.wordlist = self.load_wordlist()
        self.dark_mode = True
        self.setup_ui()
        self.setup_styles()
        self.load_saved_passwords()
        self.show()

    def load_wordlist(self):
        default_words = [
            "apple", "banana", "cherry", "dragon", "elephant", "falcon",
            "giraffe", "hunter", "island", "jungle", "knight", "lizard",
            "mountain", "ninja", "octopus", "penguin", "queen", "rocket",
            "sunset", "tiger", "unicorn", "viking", "wizard", "xylophone",
            "yacht", "zebra"
        ]
        try:
            if os.path.exists(WORDLIST_FILE):
                with open(WORDLIST_FILE, 'r') as f:
                    return [word.strip() for word in f.readlines() if word.strip()]
            return default_words
        except:
            return default_words

    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Set application font
        font = QFont("Segoe UI", 10)
        self.setFont(font)

        # Main tabs
        self.tabs = QTabWidget()
        self.tabs.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        
        # Password Generator Tab
        self.setup_password_tab()
        
        # Passphrase Generator Tab
        self.setup_passphrase_tab()
        
        # Saved Passwords Tab
        self.setup_saved_passwords_tab()
        
        layout.addWidget(self.tabs)
        self.setup_footer(layout)

    def setup_password_tab(self):
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        tab_layout.setSpacing(15)

        # Settings Group
        settings_group = QGroupBox("⚙️ Password Settings")
        settings_group.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        settings_layout = QVBoxLayout()
        settings_layout.setSpacing(10)

        # Length Control
        length_group = QWidget()
        length_layout = QHBoxLayout(length_group)
        length_layout.setContentsMargins(0, 0, 0, 0)
        length_label = QLabel("Length:")
        length_label.setFont(QFont("Segoe UI", 10))
        self.length_slider = QSlider(Qt.Orientation.Horizontal)
        self.length_slider.setRange(8, 64)
        self.length_slider.setValue(16)
        self.length_label = QLabel("16")
        self.length_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.length_slider.valueChanged.connect(lambda v: self.length_label.setText(str(v)))
        length_layout.addWidget(length_label)
        length_layout.addWidget(self.length_slider)
        length_layout.addWidget(self.length_label)
        settings_layout.addWidget(length_group)

        # Character Options
        char_group = QWidget()
        char_layout = QHBoxLayout(char_group)
        char_layout.setContentsMargins(0, 0, 0, 0)
        
        self.upper_check = self.create_checkbox("A-Z", True)
        self.lower_check = self.create_checkbox("a-z", True)
        self.numbers_check = self.create_checkbox("0-9", True)
        self.symbols_check = self.create_checkbox("!@#$", False)
        
        char_layout.addWidget(self.upper_check)
        char_layout.addWidget(self.lower_check)
        char_layout.addWidget(self.numbers_check)
        char_layout.addWidget(self.symbols_check)
        settings_layout.addWidget(char_group)

        # Keyword
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("Add custom word (optional)")
        self.keyword_input.setFont(QFont("Segoe UI", 10))
        settings_layout.addWidget(QLabel("Custom Keyword:"))
        settings_layout.addWidget(self.keyword_input)

        # Buttons
        btn_group = QWidget()
        btn_layout = QHBoxLayout(btn_group)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        
        generate_btn = self.create_button("✨ Generate", self.generate_password)
        save_btn = self.create_button("💾 Save", self.save_password)
        erase_btn = self.create_button("🧹 Erase", self.erase_password)
        
        btn_layout.addWidget(generate_btn)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(erase_btn)
        settings_layout.addWidget(btn_group)

        settings_group.setLayout(settings_layout)
        tab_layout.addWidget(settings_group)

        # Output
        output_group = QGroupBox("🔑 Generated Password")
        output_group.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        output_layout = QVBoxLayout()
        
        self.password_output = QLineEdit()
        self.password_output.setReadOnly(True)
        self.password_output.setFont(QFont("Consolas", 12))
        
        copy_btn = self.create_button("📋 Copy", lambda: self.copy_to_clipboard(self.password_output))
        
        output_btn_layout = QHBoxLayout()
        output_btn_layout.addWidget(self.password_output, 4)
        output_btn_layout.addWidget(copy_btn, 1)
        output_layout.addLayout(output_btn_layout)
        output_group.setLayout(output_layout)
        tab_layout.addWidget(output_group)

        # Analysis
        analysis_group = QGroupBox("📊 Security Analysis")
        analysis_group.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        analysis_layout = QVBoxLayout()
        
        self.strength_meter = QProgressBar()
        self.strength_meter.setRange(0, 100)
        self.strength_meter.setTextVisible(True)
        self.strength_meter.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.entropy_label = QLabel("Entropy: 0 bits")
        self.crack_time_label = QLabel("Estimated crack time: N/A")
        
        analysis_layout.addWidget(QLabel("Strength:"))
        analysis_layout.addWidget(self.strength_meter)
        analysis_layout.addWidget(self.entropy_label)
        analysis_layout.addWidget(self.crack_time_label)
        analysis_group.setLayout(analysis_layout)
        tab_layout.addWidget(analysis_group)

        self.tabs.addTab(tab, "🔐 Password")

    def setup_passphrase_tab(self):
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        tab_layout.setSpacing(15)

        # Settings Group
        settings_group = QGroupBox("⚙️ Passphrase Settings")
        settings_group.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        settings_layout = QVBoxLayout()
        settings_layout.setSpacing(10)

        # Word Count
        word_group = QWidget()
        word_layout = QHBoxLayout(word_group)
        word_layout.setContentsMargins(0, 0, 0, 0)
        word_label = QLabel("Words:")
        word_label.setFont(QFont("Segoe UI", 10))
        self.word_slider = QSlider(Qt.Orientation.Horizontal)
        self.word_slider.setRange(4, 8)
        self.word_slider.setValue(4)
        self.word_label = QLabel("4")
        self.word_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.word_slider.valueChanged.connect(lambda v: self.word_label.setText(str(v)))
        word_layout.addWidget(word_label)
        word_layout.addWidget(self.word_slider)
        word_layout.addWidget(self.word_label)
        settings_layout.addWidget(word_group)

        # Separator
        self.separator_input = QLineEdit("-")
        self.separator_input.setMaxLength(1)
        self.separator_input.setFont(QFont("Segoe UI", 10))
        settings_layout.addWidget(QLabel("Separator:"))
        settings_layout.addWidget(self.separator_input)

        # Numbers
        self.number_check = self.create_checkbox("Add random number", True)
        settings_layout.addWidget(self.number_check)

        # Buttons
        btn_group = QWidget()
        btn_layout = QHBoxLayout(btn_group)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        
        generate_btn = self.create_button("✨ Generate Passphrase", self.generate_passphrase)
        erase_btn = self.create_button("🧹 Erase", lambda: self.passphrase_output.clear())
        
        btn_layout.addWidget(generate_btn)
        btn_layout.addWidget(erase_btn)
        settings_layout.addWidget(btn_group)

        settings_group.setLayout(settings_layout)
        tab_layout.addWidget(settings_group)

        # Output
        output_group = QGroupBox("🔤 Passphrase")
        output_group.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        output_layout = QVBoxLayout()
        
        self.passphrase_output = QLineEdit()
        self.passphrase_output.setReadOnly(True)
        self.passphrase_output.setFont(QFont("Consolas", 12))
        
        copy_btn = self.create_button("📋 Copy", lambda: self.copy_to_clipboard(self.passphrase_output))
        save_btn = self.create_button("💾 Save", lambda: self.save_password(self.passphrase_output.text()))
        
        output_btn_layout = QHBoxLayout()
        output_btn_layout.addWidget(self.passphrase_output, 4)
        output_btn_layout.addWidget(copy_btn, 1)
        output_btn_layout.addWidget(save_btn, 1)
        output_layout.addLayout(output_btn_layout)
        output_group.setLayout(output_layout)
        tab_layout.addWidget(output_group)

        self.tabs.addTab(tab, "📝 Passphrase")

    def setup_saved_passwords_tab(self):
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        tab_layout.setSpacing(15)

        # Saved Passwords List
        self.saved_list = QListWidget()
        self.saved_list.setFont(QFont("Consolas", 10))
        self.saved_list.itemDoubleClicked.connect(self.copy_saved_password)
        tab_layout.addWidget(self.saved_list)

        # Buttons
        btn_group = QWidget()
        btn_layout = QHBoxLayout(btn_group)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        
        export_btn = self.create_button("📤 Export", self.export_passwords)
        clear_all_btn = self.create_button("🗑️ Clear All", self.clear_saved_passwords)
        clear_selected_btn = self.create_button("✖️ Clear Selected", self.clear_selected_password)
        theme_btn = self.create_button("🌙 Toggle Theme", self.toggle_theme)
        
        btn_layout.addWidget(export_btn)
        btn_layout.addWidget(clear_selected_btn)
        btn_layout.addWidget(clear_all_btn)
        btn_layout.addWidget(theme_btn)
        tab_layout.addWidget(btn_group)

        self.tabs.addTab(tab, "💾 Saved")

    def setup_footer(self, layout):
        footer = QLabel("© 2025 PassCraft | v1.0")
        footer.setFont(QFont("Segoe UI", 8))
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)

    def create_button(self, text, action):
        btn = QPushButton(text)
        btn.setFont(QFont("Segoe UI", 10))
        btn.clicked.connect(action)
        return btn

    def create_checkbox(self, text, checked):
        cb = QCheckBox(text)
        cb.setFont(QFont("Segoe UI", 10))
        cb.setChecked(checked)
        return cb

    def generate_password(self):
        charset = ""
        if self.upper_check.isChecked(): charset += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if self.lower_check.isChecked(): charset += "abcdefghijklmnopqrstuvwxyz"
        if self.numbers_check.isChecked(): charset += "0123456789"
        if self.symbols_check.isChecked(): charset += "!@#$%^&*"
        
        if not charset:
            QMessageBox.warning(self, "Error", "Please select at least one character set!")
            return None
        
        length = self.length_slider.value()
        keyword = self.keyword_input.text()
        
        # Generate random part first
        random_part = ''.join(secrets.choice(charset) for _ in range(length - len(keyword)))
        random_part = ''.join(secrets.SystemRandom().sample(random_part, len(random_part)))
        
        # Combine with keyword (inserted at random position)
        insert_pos = secrets.randbelow(len(random_part) + 1)
        password = random_part[:insert_pos] + keyword + random_part[insert_pos:]
        
        self.password_output.setText(password)
        self.analyze_password(password)
        return password

    def generate_passphrase(self):
        words = [secrets.choice(self.wordlist).capitalize() 
                for _ in range(self.word_slider.value())]
        
        if self.number_check.isChecked():
            words.append(str(secrets.randbelow(90) + 10))
            
        separator = self.separator_input.text()[:1] or "-"
        passphrase = separator.join(words)
        
        self.passphrase_output.setText(passphrase)
        self.analyze_password(passphrase)
        return passphrase

    def analyze_password(self, password):
        if not password:
            return
            
        # Calculate entropy
        pool = 0
        if any(c.isupper() for c in password): pool += 26
        if any(c.islower() for c in password): pool += 26
        if any(c.isdigit() for c in password): pool += 10
        if any(not c.isalnum() for c in password): pool += 32
        entropy = math.log2(pool ** len(password)) if pool > 0 else 0
        
        # Strength score (0-100)
        length_bonus = min(40, len(password) * 2)
        complexity_bonus = min(60, entropy * 1.5)
        score = int(min(100, length_bonus + complexity_bonus))  # Convert to int
        
        # Determine strength level
        if score < 20:
            strength_text = "Very Weak"
            strength_color = "#ff0000"  # Red
        elif score < 40:
            strength_text = "Weak"
            strength_color = "#ff5555"  # Light Red
        elif score < 60:
            strength_text = "Moderate"
            strength_color = "#ffb86c"  # Orange
        elif score < 80:
            strength_text = "Strong"
            strength_color = "#50fa7b"  # Green
        elif score < 95:
            strength_text = "Very Strong"
            strength_color = "#00bfff"  # Blue
        else:
            strength_text = "Extremely Strong"
            strength_color = "#8a2be2"  # Purple
        
        # Calculate crack time separately
        crack_speed = 1e9  # 1 billion guesses per second
        combinations = pool ** len(password)
        seconds = combinations / crack_speed
        
        if seconds < 1:
            crack_time = "Instant"
        elif seconds < 60:
            crack_time = f"{int(seconds)} seconds"
        elif seconds < 3600:
            crack_time = f"{int(seconds/60)} minutes"
        elif seconds < 86400:
            crack_time = f"{int(seconds/3600)} hours"
        elif seconds < 31536000:  # 1 year
            crack_time = f"{int(seconds/86400)} days"
        elif seconds < 3153600000:  # 100 years
            crack_time = f"{int(seconds/31536000)} years"
        else:
            crack_time = "Centuries"
        
        # Update UI
        self.entropy_label.setText(f"Entropy: {entropy:.1f} bits")
        self.crack_time_label.setText(f"Estimated crack time: {crack_time}")
        
        # Strength meter
        self.strength_meter.setValue(score)
        self.strength_meter.setFormat(f"{strength_text} ({score}%)")
        self.strength_meter.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {strength_color};
                border-radius: 5px;
                text-align: center;
                color: {'#000000' if score > 50 else '#ffffff'};
            }}
            QProgressBar::chunk {{
                background-color: {strength_color};
                width: 10px;
            }}
        """)

    def copy_to_clipboard(self, widget):
        text = widget.text()
        if not text:
            return
            
        QApplication.clipboard().setText(text)
        QToolTip.showText(widget.mapToGlobal(widget.rect().bottomLeft()), "Copied!", msecShowTime=1000)

    def erase_password(self):
        self.password_output.clear()
        self.strength_meter.setValue(0)
        self.entropy_label.setText("Entropy: 0 bits")
        self.crack_time_label.setText("Estimated crack time: N/A")

    def save_password(self, password=None):
        if not password:
            password = self.password_output.text()
        
        if not password:
            QMessageBox.warning(self, "Error", "No password to save")
            return
            
        name, ok = QInputDialog.getText(self, "Save Password", "Enter a name for this password:")
        if not ok or not name:
            return
            
        self.saved_passwords.append({
            'name': name,
            'password': password,
            'type': 'passphrase' if ' ' in password or '-' in password else 'password',
            'date': datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        
        try:
            with open(SAVED_PASSWORDS_FILE, 'w') as f:
                json.dump(self.saved_passwords, f)
            self.load_saved_passwords()
            QMessageBox.information(self, "Success", "Password saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save password: {str(e)}")

    def load_saved_passwords(self):
        try:
            if os.path.exists(SAVED_PASSWORDS_FILE):
                with open(SAVED_PASSWORDS_FILE, 'r') as f:
                    self.saved_passwords = json.load(f)
            
            self.saved_list.clear()
            for item in self.saved_passwords:
                list_item = QListWidgetItem(f"{item['name']} - {item['password']} ({item['date']})")
                list_item.setData(Qt.ItemDataRole.UserRole, item['password'])
                self.saved_list.addItem(list_item)
        except:
            self.saved_passwords = []

    def copy_saved_password(self, item):
        password = item.data(Qt.ItemDataRole.UserRole)
        QApplication.clipboard().setText(password)
        QToolTip.showText(self.mapToGlobal(self.saved_list.rect().topLeft()), "Copied!", msecShowTime=1000)

    def clear_saved_passwords(self):
        reply = QMessageBox.question(
            self, "Confirm", 
            "Are you sure you want to delete ALL saved passwords?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.saved_passwords = []
            try:
                with open(SAVED_PASSWORDS_FILE, 'w') as f:
                    json.dump([], f)
                self.saved_list.clear()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to clear passwords: {str(e)}")

    def clear_selected_password(self):
        selected = self.saved_list.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Error", "No password selected")
            return
            
        reply = QMessageBox.question(
            self, "Confirm", 
            "Delete the selected password?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.saved_passwords.pop(selected)
                with open(SAVED_PASSWORDS_FILE, 'w') as f:
                    json.dump(self.saved_passwords, f)
                self.load_saved_passwords()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete password: {str(e)}")

    def export_passwords(self):
        if not self.saved_passwords:
            QMessageBox.warning(self, "Error", "No passwords to export")
            return
            
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Export Passwords", "", 
            "JSON Files (*.json);;CSV Files (*.csv)"
        )
        
        if not file_name:
            return
            
        try:
            if file_name.endswith('.csv'):
                with open(file_name, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Name', 'Password', 'Type', 'Date'])
                    for item in self.saved_passwords:
                        writer.writerow([item['name'], item['password'], item['type'], item['date']])
            else:
                if not file_name.endswith('.json'):
                    file_name += '.json'
                with open(file_name, 'w') as f:
                    json.dump(self.saved_passwords, f, indent=2)
            
            QMessageBox.information(self, "Success", "Passwords exported successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export passwords: {str(e)}")

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.setup_styles()

    def setup_styles(self):
        if self.dark_mode:
            # Dark theme
            self.setStyleSheet("""
                QWidget {
                    background-color: #1e1e2e;
                    color: #cdd6f4;
                }
                QGroupBox {
                    border: 2px solid #89b4fa;
                    border-radius: 8px;
                    margin-top: 10px;
                    padding-top: 15px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                    color: #89b4fa;
                }
                QLineEdit, QListWidget {
                    background-color: #313244;
                    color: #cdd6f4;
                    border: 1px solid #45475a;
                    border-radius: 5px;
                    padding: 5px;
                }
                QPushButton {
                    background-color: #585b70;
                    color: #cdd6f4;
                    border: 1px solid #6c7086;
                    border-radius: 5px;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #6c7086;
                }
                QCheckBox {
                    spacing: 5px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                }
                QSlider::groove:horizontal {
                    height: 6px;
                    background: #45475a;
                    border-radius: 3px;
                }
                QSlider::handle:horizontal {
                    width: 16px;
                    height: 16px;
                    margin: -5px 0;
                    background: #89b4fa;
                    border-radius: 8px;
                }
                QTabWidget::pane {
                    border: 1px solid #45475a;
                }
                QTabBar::tab {
                    background: #313244;
                    color: #cdd6f4;
                    padding: 5px 10px;
                    border: 1px solid #45475a;
                    border-bottom: none;
                    border-top-left-radius: 5px;
                    border-top-right-radius: 5px;
                }
                QTabBar::tab:selected {
                    background: #45475a;
                    color: #89b4fa;
                }
                QListWidget::item:selected {
                    background: #585b70;
                }
            """)
        else:
            # Light theme
            self.setStyleSheet("""
                QWidget {
                    background-color: #fafafa;
                    color: #4a4a4a;
                }
                QGroupBox {
                    border: 2px solid #1e88e5;
                    border-radius: 8px;
                    margin-top: 10px;
                    padding-top: 15px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                    color: #1e88e5;
                }
                QLineEdit, QListWidget {
                    background-color: #ffffff;
                    color: #333333;
                    border: 1px solid #e0e0e0;
                    border-radius: 5px;
                    padding: 5px;
                }
                QPushButton {
                    background-color: #e0e0e0;
                    color: #333333;
                    border: 1px solid #bdbdbd;
                    border-radius: 5px;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #bdbdbd;
                }
                QCheckBox {
                    spacing: 5px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                }
                QSlider::groove:horizontal {
                    height: 6px;
                    background: #e0e0e0;
                    border-radius: 3px;
                }
                QSlider::handle:horizontal {
                    width: 16px;
                    height: 16px;
                    margin: -5px 0;
                    background: #1e88e5;
                    border-radius: 8px;
                }
                QTabWidget::pane {
                    border: 1px solid #e0e0e0;
                }
                QTabBar::tab {
                    background: #f5f5f5;
                    color: #666666;
                    padding: 5px 10px;
                    border: 1px solid #e0e0e0;
                    border-bottom: none;
                    border-top-left-radius: 5px;
                    border-top-right-radius: 5px;
                }
                QTabBar::tab:selected {
                    background: #ffffff;
                    color: #1e88e5;
                }
                QListWidget::item:selected {
                    background: #e0e0e0;
                }
            """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PasswordGenerator()
    sys.exit(app.exec())
