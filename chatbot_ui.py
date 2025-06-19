import sys
import subprocess
from PySide6.QtWidgets import (
    QPlainTextEdit, QTextEdit, QPushButton, QVBoxLayout,
    QLabel, QWidget, QHBoxLayout, QSizePolicy, QScrollArea, QApplication
)
from PySide6.QtCore import Qt


class ChatWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Heading
        heading = QLabel("ASK")
        heading.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(heading)

        # Scroll area for chat history
        self.chat_area = QVBoxLayout()
        self.chat_area.setAlignment(Qt.AlignTop)

        scroll_content = QWidget()
        scroll_content.setLayout(self.chat_area)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        # Input area
        self.input_box = QTextEdit()
        self.input_box.setFixedHeight(60)
        self.input_box.textChanged.connect(self.adjust_textbox_height)
        self.input_box.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.MinimumExpanding
        )

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_box)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)

    def adjust_textbox_height(self):
        doc_height = self.input_box.document().size().height()
        line_height = self.input_box.fontMetrics().height()
        max_lines = 10
        height = int(min(doc_height, max_lines * line_height + 10))
        self.input_box.setFixedHeight(height)

    def add_chat_message(self, role, message):
        # Create message container
        msg_layout = QVBoxLayout()
        msg_widget = QWidget()
        msg_widget.setLayout(msg_layout)

        role_label = QLabel(f"{role}")
        role_label.setStyleSheet("font-weight: bold;")

        text_label = QLabel(message)
        text_label.setWordWrap(True)
        text_label.setStyleSheet(
            f"""
            padding: 8px;
            border-radius: 8px;
            color: black;
            background-color: {
                '#e0f7fa' if role == 'Assistant' else '#f0f0f0'
            };
            """
        )
        text_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        msg_layout.addWidget(role_label)
        msg_layout.addWidget(text_label)

        alignment_layout = QHBoxLayout()
        alignment_layout.setContentsMargins(0, 5, 0, 5)
        if role == "User":
            alignment_layout.addWidget(msg_widget, alignment=Qt.AlignLeft)
            alignment_layout.addStretch()
        else:
            alignment_layout.addStretch()
            alignment_layout.addWidget(msg_widget, alignment=Qt.AlignRight)

        self.chat_area.addLayout(alignment_layout)

    def send_message(self):
        text = self.input_box.toPlainText().strip()
        if text:
            self.add_chat_message("User", text)
            self.add_chat_message("Assistant", "Hello")
            self.input_box.clear()
            self.parent().right_output.update_output(text)


class OutputWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Output Heading
        heading = QLabel("Output")
        heading.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(heading)

        # Editable Output Box
        self.output_box = QTextEdit()
        layout.addWidget(self.output_box)

        # Command Prompt Heading
        terminal_label = QLabel("Command Prompt")
        terminal_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 20px;")
        layout.addWidget(terminal_label)

        # Terminal Output Display
        self.terminal_output = QPlainTextEdit()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setStyleSheet("background-color: black; color: white;")
        layout.addWidget(self.terminal_output, 2)

        # Terminal Input + Run Button
        input_layout = QHBoxLayout()
        self.terminal_input = QPlainTextEdit()
        self.terminal_input.setPlaceholderText("Enter command...")
        self.terminal_input.setFixedHeight(50)
        self.terminal_input.keyPressEvent = self.handle_keypress_override

        run_button = QPushButton("Run")
        run_button.clicked.connect(self.run_command)

        input_layout.addWidget(self.terminal_input)
        input_layout.addWidget(run_button)
        layout.addLayout(input_layout)

    def update_output(self, user_input):
        self.output_box.append(f"User asked: {user_input}")

    def handle_keypress_override(self, event):
        # Support Shift+Enter for newline, Enter for command execution
        if event.key() == Qt.Key_Return and not (event.modifiers() & Qt.ShiftModifier):
            self.run_command()
        else:
            # Default behavior
            QPlainTextEdit.keyPressEvent(self.terminal_input, event)

    def run_command(self):
        command = self.terminal_input.toPlainText().strip()
        if not command:
            return

        try:
            result = subprocess.run(
                command, shell=True, check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            output = result.stdout + result.stderr
        except Exception as e:
            output = f"Error: {str(e)}"

        self.terminal_output.appendPlainText(f"> {command}\n{output}")
        self.terminal_input.clear()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LLM Chatbot UI")

        main_layout = QHBoxLayout(self)

        # Left: Chat Area
        self.chat_widget = ChatWidget()
        self.chat_widget.setMinimumWidth(400)
        self.chat_widget.setMaximumWidth(600)

        # Right: Output Area
        self.right_output = OutputWidget()

        self.chat_widget.setParent(self)
        self.right_output.setParent(self)

        main_layout.addWidget(self.chat_widget, 2)
        main_layout.addWidget(self.right_output, 3)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.resize(1000, 600)
    win.show()
    sys.exit(app.exec())
