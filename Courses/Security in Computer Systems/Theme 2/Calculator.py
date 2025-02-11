import sys
import hashlib
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QButtonGroup, QRadioButton
)

class HashGeneratorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hash Generator")
        self.setGeometry(100, 100, 400, 250)

        # Layout
        self.layout = QVBoxLayout()

        # Input Field
        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("Enter text here...")
        self.layout.addWidget(self.input_field)

        # Radio Buttons for Hash Algorithm Selection
        self.hash_group = QButtonGroup(self)
        self.sha256_btn = QRadioButton("SHA-256")
        self.sha3_256_btn = QRadioButton("SHA3-256")
        self.md5_btn = QRadioButton("MD5")
        self.sha1_btn = QRadioButton("SHA1")

        self.layout.addWidget(self.sha256_btn)
        self.layout.addWidget(self.sha3_256_btn)
        self.layout.addWidget(self.md5_btn)
        self.layout.addWidget(self.sha1_btn)

        self.hash_group.addButton(self.sha256_btn)
        self.hash_group.addButton(self.sha3_256_btn)
        self.hash_group.addButton(self.md5_btn)
        self.hash_group.addButton(self.sha1_btn)

        self.sha256_btn.setChecked(True)  # Default selection

        # Generate Hash Button
        self.generate_btn = QPushButton("Generate Hash")
        self.generate_btn.clicked.connect(self.generate_hash)
        self.layout.addWidget(self.generate_btn)

        # Clear Button
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_fields)
        self.layout.addWidget(self.clear_btn)

        # Output Label
        self.output_label = QLabel("Generated hash will appear here.")
        self.layout.addWidget(self.output_label)

        self.setLayout(self.layout)

    def generate_hash(self):
        text = self.input_field.text().encode('utf-8')
        if self.sha256_btn.isChecked():
            hashed = hashlib.sha256(text).hexdigest()
        elif self.sha3_256_btn.isChecked():
            hashed = hashlib.sha3_256(text).hexdigest()
        elif self.md5_btn.isChecked():
            hashed = hashlib.md5(text).hexdigest()
        elif self.sha1_btn.isChecked():
            hashed = hashlib.sha1(text).hexdigest()
        else:
            hashed = "No algorithm selected"
        
        self.output_label.setText(f"Hash: {hashed}")

    def clear_fields(self):
        self.input_field.clear()
        self.output_label.setText("Generated hash will appear here.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HashGeneratorApp()
    window.show()
    sys.exit(app.exec())
