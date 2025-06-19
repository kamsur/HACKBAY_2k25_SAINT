from typing import Any
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QScrollArea, QFrame, QSizePolicy, QFileDialog
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from agno.agent import RunResponse

import sys
import os
import re
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from tools.extract_kanban_from_markdown import extract_sections_and_done_items
from tools.GitHubTool import GithubTool
import agents.ComplianceManager as ComplianceManager

class ChatMessage(QWidget):
    def __init__(self, sender, text, is_user):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        # Message container
        msg_layout = QVBoxLayout()
        msg_layout.setContentsMargins(0, 0, 0, 0)
        msg_widget = QWidget()
        msg_widget.setLayout(msg_layout)

        # Sender label
        sender_label = QLabel(sender)
        sender_label.setStyleSheet("font-size: 12px; color: #666; font-weight: bold;")

        # Message bubble
        message_label = QLabel(text)
        message_label.setWordWrap(True)
        message_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        message_label.setStyleSheet(
            f"""
            padding: 10px;
            border-radius: 16px;
            color: black;
            font-size: 13px;
            background-color: {'#dcf8c6' if is_user else '#e6e6e6'};
            """
        )

        # Choose alignment
        alignment = Qt.AlignRight if not is_user else Qt.AlignLeft

        # Apply alignment to both labels
        msg_layout.addWidget(sender_label, alignment=alignment)
        msg_layout.addWidget(message_label, alignment=alignment)

        # Alignment layout
        alignment_layout = QHBoxLayout()
        alignment_layout.setContentsMargins(0, 5, 0, 5)
        if is_user:
            alignment_layout.addWidget(msg_widget, alignment=Qt.AlignLeft)
            alignment_layout.addStretch()
        else:
            alignment_layout.addStretch()
            alignment_layout.addWidget(msg_widget, alignment=Qt.AlignRight)

        self.setLayout(alignment_layout)


class AgentWorker(QThread):
    finished = Signal(str)

    def __init__(self, text, tester_first_run=False):
        super().__init__()
        self.text = text
        self.tester_first_run = tester_first_run

    def run(self):

        if sys.argv[1] == '1':
            from agents.ProductManager import agent
            response = agent.run(self.text)
            self.finished.emit(response.content)
            with open("AppData\\KanbanBoardData.md", "w") as file:
                file.write(response.content)
        elif sys.argv[1] == '2': # developer agent todo
            from agents.SoftwareDeveloper import agent
            response = agent.run(self.text)
            self.finished.emit(response.content)
        elif sys.argv[1] == '3': # tester agent todo
            from agents.SoftwareTester import agent
            response = agent.run(self.text)
            self.finished.emit(response.content)
        elif sys.argv[1] == '4': # optimiser agent todo
            pass
        elif sys.argv[1] == '5': # compliance agent todo
            pass


class ComplianceWorker(QThread):
    finished = Signal(str)
    def __init__(self, text):
        super().__init__()
        self.text = text
    def run(self):
        try:
            response = ComplianceManager.query_llm(self.text)
            self.finished.emit(response)
        except Exception as e:
            self.finished.emit(f"[Compliance Error] {str(e)}")

class ComplianceUploadWorker(QThread):
    finished = Signal(str)
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
    def run(self):
        try:
            result = ComplianceManager.upload_and_index_file(self.file_path)
            self.finished.emit(f"[Upload] {result}")
        except Exception as e:
            self.finished.emit(f"[Upload Error] {str(e)}")

class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChatGPT Clone UI")
        self.setFixedSize(400, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                font-family: 'Segoe UI', sans-serif;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Chat wrapper
        chat_wrapper = QFrame()
        chat_wrapper.setStyleSheet("""
            background-color: white;
            border-radius: 12px;
        """)
        chat_wrapper.setFrameShape(QFrame.StyledPanel)
        chat_layout = QVBoxLayout(chat_wrapper)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)

        # Scroll area for messages
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background-color: #fafafa; border:none;")
        self.scroll_area_widget = QWidget()
        self.scroll_area_layout = QVBoxLayout(self.scroll_area_widget)
        self.scroll_area_layout.setContentsMargins(15, 15, 15, 15)
        self.scroll_area_layout.setSpacing(8)
        self.scroll_area_layout.addStretch()
        self.scroll_area.setWidget(self.scroll_area_widget)
        chat_layout.addWidget(self.scroll_area)

        # Responding label (hidden by default)
        self.responding_label = QLabel("Responding...")
        self.responding_label.setAlignment(Qt.AlignCenter)
        self.responding_label.setStyleSheet("color: #007bff; font-size: 13px; padding: 2px;")
        self.responding_label.setVisible(False)
        chat_layout.addWidget(self.responding_label)

        # Input box
        input_box = QFrame()
        input_box.setStyleSheet("background-color: white; border-top: 1px solid #ddd;")
        input_box.setFixedHeight(70)  # Increased height
        input_layout = QHBoxLayout(input_box)
        input_layout.setContentsMargins(10, 10, 10, 10)

        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type a message...")
        self.chat_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 20px;
                padding: 12px;
                font-size: 14px;
                color: black;
            }
            QLineEdit:focus {
                border-color: #007bff;
            }
        """)
        self.chat_input.setMinimumHeight(40)  # Increased input field height
        self.chat_input.returnPressed.connect(self.send_message)

        send_button = QPushButton("Send")
        send_button.setCursor(Qt.PointingHandCursor)
        send_button.setMinimumHeight(40)  # Increased button height
        send_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 20px;
                padding: 0px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        send_button.clicked.connect(self.send_message)

        # Add upload button for compliance agent (right of send)
        self.upload_button = QPushButton("\U0001F4CE")  # 📎 attach symbol
        self.upload_button.setCursor(Qt.PointingHandCursor)
        self.upload_button.setMinimumHeight(40)
        self.upload_button.setFixedWidth(48)
        self.upload_button.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #333;
                border: none;
                border-radius: 20px;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #bdbdbd;
            }
        """)
        self.upload_button.clicked.connect(self.upload_document)
        if len(sys.argv) > 1 and sys.argv[1] == '5':
            input_layout.addWidget(self.upload_button)
        self.upload_button.setVisible(len(sys.argv) > 1 and sys.argv[1] == '5')

        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(send_button)

        chat_layout.addWidget(input_box)
        main_layout.addWidget(chat_wrapper)

        self.agent_thread = None
        self.tester_first_run = True
        # If tester agent, run generate_test_code immediately
        if len(sys.argv) > 1 and sys.argv[1] == '3':
            self.append_message("[Test Generation and Execution Output]", 'user')
            self.responding_label.setText("Responding...")
            self.responding_label.setVisible(True)
            self.agent_thread = AgentWorker("", tester_first_run=True)
            self.agent_thread.finished.connect(self._show_response)
            self.agent_thread.start()
            self.tester_first_run = False

    def append_message(self, text, sender_type):
        # Change sender label for compliance agent
        if len(sys.argv) > 1 and sys.argv[1] == '5':
            sender = "Me" if sender_type == 'user' else "Compliance Manager"
        else:
            sender = "Me" if sender_type == 'user' else "Agentic Product Manager"
        is_user = sender_type == 'user'
        if sender_type == 'user':
            sender = "Me"
        else:
            if sys.argv[1] == '1':
                sender = "Agentic Product Manager"
            elif sys.argv[1] == '2':
                sender = "Agentic Developer"
            elif sys.argv[1] == '3':
                sender = "Agentic Tester"
            elif sys.argv[1] == '4':
                sender = "Agentic Optimiser"
            elif sys.argv[1] == '5':
                sender = "Compliance Manager"
                
        message_widget = ChatMessage(sender, text, is_user)
        self.scroll_area_layout.insertWidget(self.scroll_area_layout.count()-1, message_widget)
        if sender_type == 'user':
            QTimer.singleShot(100, lambda: self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum()))

    def upload_document(self):
        self.responding_label.setText("Uploading...")
        self.responding_label.setVisible(True)
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilters(["PDF Files (*.pdf)", "Text Files (*.txt)", "CSV Files (*.csv)"])
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            self.upload_thread = ComplianceUploadWorker(file_path)
            self.upload_thread.finished.connect(self._show_upload_result)
            self.upload_thread.start()
        else:
            self.responding_label.setText("Responding...")
            self.responding_label.setVisible(False)

    def _show_upload_result(self, result):
        self.append_message(result, 'bot')
        self.responding_label.setText("Responding...")
        self.responding_label.setVisible(False)
        self.upload_thread = None

    def send_message(self):
        text = self.chat_input.text().strip()
        if not text:
            return
        self.append_message(text, 'user')
        self.chat_input.clear()
        self.responding_label.setText("Responding...")
        self.responding_label.setVisible(True)

        if sys.argv[1] == '1': # Product Manager Agent
            # regex to check intention
            keywords1 = ['push', 'post', 'add', 'append']
            keywords2 = ['board', 'project']

            if any(k1 in text for k1 in keywords1) and any(k2 in text for k2 in keywords2):
                with open(r"AppData\KanbanBoardData.md", "r", encoding="utf-8") as f:
                    markdown_content = f.read()

                sections_list, _ = extract_sections_and_done_items(markdown_content)

                pattern = r'\*\*Title\*\*:\s*(.*?)\n(.*)'

                GITHUB_TOKEN = "TOKEN"
                OWNER = "kamsur"
                REPO = "HACKBAY_2k25_SAINT"
                TARGET_PROJECT = "HACKBAY_2025"

                tool = GithubTool(OWNER, REPO, GITHUB_TOKEN)
                

                
                for i, section in enumerate(sections_list, 1):                    
                    match = re.search(pattern, section, re.DOTALL)
                    if match:
                        title = match.group(1).strip()
                        rest_of_text = match.group(2).strip()

                        tool.post_to_kanban_board(TARGET_PROJECT, title, rest_of_text, "Product Backlog")

                    
            else:
                self.agent_thread = AgentWorker(text)
                self.agent_thread.finished.connect(self._show_response)
                self.agent_thread.start()

        elif sys.argv[1] == '2': # developer agent todo
            self.agent_thread = AgentWorker(text)
            self.agent_thread.finished.connect(self._show_response)
            self.agent_thread.start()
        elif sys.argv[1] == '3': # tester agent
            self.agent_thread = AgentWorker(text, tester_first_run=False)
            self.agent_thread.finished.connect(self._show_response)
            self.agent_thread.start()
        elif sys.argv[1] == '4': # optimiser agent todo
            pass
        elif sys.argv[1] == '5': # compliance agent
            self.compliance_thread = ComplianceWorker(text)
            self.compliance_thread.finished.connect(self._show_response)
            self.compliance_thread.start()
       


    def _show_response(self, content):
        self.append_message(content, 'bot')
        self.responding_label.setVisible(False)
        self.agent_thread = None


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec())
