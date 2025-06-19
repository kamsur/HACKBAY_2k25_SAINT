import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, QObject, Slot
from chatbot_ui import MainWindow
from PySide6.QtWebChannel import QWebChannel


class LoginHandler(QObject):
    def __init__(self, login_window):
        super().__init__()
        self.login_window = login_window

    @Slot(str, str)
    def validateCredentials(self, username, password):
        # Replace this with your actual authentication logic
        if username == "admin" and password == "password":
            self.login_window.login_successful()
        else:
            # Call JavaScript function to show error
            self.login_window.browser.page().runJavaScript(
                "showError('Invalid credentials')"
            )


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 600, 500)

        self.browser = QWebEngineView()
        
        # Set up web channel
        self.channel = QWebChannel()
        self.login_handler = LoginHandler(self)
        self.channel.registerObject("loginHandler", self.login_handler)
        self.browser.page().setWebChannel(self.channel)

        # Load the HTML file
        html_path = os.path.abspath("login.html")
        self.browser.setUrl(QUrl.fromLocalFile(html_path))

        self.setCentralWidget(self.browser)

    def login_successful(self):
        self.close()
        self.main_window = MainWindow()
        self.main_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginWindow()
    login.show()
    sys.exit(app.exec())
