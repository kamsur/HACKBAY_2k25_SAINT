import sys
import subprocess
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QDesktopServices, QCursor
from PySide6.QtCore import QUrl

class VSCodeLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Open VS Code")

        layout = QVBoxLayout()

        self.label = QLabel()
        self.label.setText(
            '<a href="#">Click here to open Visual Studio Code</a>'
        )
        self.label.setTextFormat(Qt.RichText)
        self.label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.label.setOpenExternalLinks(False)
        self.label.linkActivated.connect(self.open_vscode)

        layout.addWidget(self.label)
        self.setLayout(layout)

    def open_vscode(self):
        try:
            subprocess.Popen(['code .'])  # Assumes 'code' is in PATH
        except FileNotFoundError:
            self.label.setText("VS Code not found. Make sure 'code' is in your PATH.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VSCodeLauncher()
    window.show()
    sys.exit(app.exec())
