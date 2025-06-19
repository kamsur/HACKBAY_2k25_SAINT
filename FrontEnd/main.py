import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtCore import QObject, Slot, QUrl
import subprocess

class AgentBridge(QObject):
    @Slot(str)
    def trigger_agent(self, agent_no):
        if agent_no == 'God-Mode':
            subprocess.Popen([
                sys.executable,
                os.path.join(os.path.dirname(__file__), 'god-mode-ui.py')
            ])
        else:
            subprocess.Popen([
                    sys.executable,
                    os.path.join(os.path.dirname(__file__), 'chat_with_agent.py'),
                    str(agent_no)
                ])

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
        self.agent_bridge = AgentBridge()
        self.channel.registerObject('agentBridge', self.agent_bridge)
        self.view.page().setWebChannel(self.channel)

        # Load the HTML file
        html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'index.html'))
        self.view.load(QUrl.fromLocalFile(html_path))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 