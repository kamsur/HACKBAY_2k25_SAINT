import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtCore import QObject, Slot, QUrl, Signal
import subprocess




class Bridge(QObject):
    dataChanged = Signal(str)

    @Slot(str)
    def sendData(self, data):
        self.dataChanged.emit(data)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("S.A.I.N.T")
        self.resize(1200, 800)
        self.view = QWebEngineView(self)
        self.setCentralWidget(self.view)
        self.showMaximized()

        # Set up web channel
        self.channel = QWebChannel()
        self.bridge = Bridge()
        self.channel.registerObject('bridge', self.bridge)
        self.view.page().setWebChannel(self.channel)

        # Load the HTML file
        html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'matrix.html'))
        self.view.load(QUrl.fromLocalFile(html_path))

        # Example: send data every 2 seconds (for demo)
        from PySide6.QtCore import QTimer
        self.messages = [
            "Agent Call: Contacting Product Manager...",
            "Retrieving user stories, technical requirements, and other documentation...",
            "Initializing developer agents...",
            "Fetching open GitHub issues...",
            "Generating boilerplate code...",
            "Saving generated code...",
            "Starting tester agent...",
            "Creating unit tests...",
            "Generating additional test cases...",
            "Executing tests...",
            "Test Status: Failed.",
            "Retrying...",
            "Debugging and fixing code...",
            "Re-running tests...",
            "Test Status: Passed.",
            "Launching optimizer agent...",
            "Applying optimized data structures and improving runtime performance...",
            "Comparing performance before and after optimization...",
            "Activating compliance agent...",
            "Verifying compliance with open-source licensing and policies...",
            "Pushing final codebase to GitHub...",
            "Generating metrics...\n",
            "1250.92779040336609 seconds\n[codecarbon INFO @ 14:20:46]\nGraceful stopping: collecting and writing information.\nPlease wait a few seconds...",
            "[codecarbon INFO @ 14:20:46] Energy consumed for RAM : 0.000348 kWh. RAM Power : 10.0 W\n[codecarbon INFO @ 14:20:46] Delta energy consumed for CPU with constant : 0.000067 kWh, power : 42.5 W\n[codecarbon INFO @ 14:20:46] Energy consumed for All CPU : 0.001482 kWh\n[codecarbon INFO @ 14:20:46] Energy consumed for all GPUs : 0.000135 kWh. Total GPU Power : 6.456608125385827 W\n[codecarbon INFO @ 14:20:46] 0.001965 kWh of electricity used since the beginning.\n[codecarbon INFO @ 14:20:46] Done!",
        ]
        self.current_message_index = 0
        def send_periodic_message():
            if self.current_message_index < len(self.messages):
                message = self.messages[self.current_message_index]
                self.bridge.dataChanged.emit(message)
                self.current_message_index += 1
            else:
                self.timer.stop()
        self.timer = QTimer(self)
        self.timer.timeout.connect(send_periodic_message)
        self.timer.start(2000)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 